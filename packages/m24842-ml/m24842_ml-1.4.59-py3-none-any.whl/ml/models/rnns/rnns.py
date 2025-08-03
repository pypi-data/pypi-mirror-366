import torch
import torch.nn as nn
import torch.nn.functional as F
from einops import rearrange, repeat
from ..common import *

cuda_causal_conv1d = None
try: from causal_conv1d import causal_conv1d_fn as cuda_causal_conv1d
except: pass

class Mamba2Block(nn.Module):
    def __init__(self, d_model, d_state=128, d_conv=4,
                 expand=2, n_heads=4, chunk_size=64, device="cpu"):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state
        self.d_conv = d_conv
        self.expand = expand
        self.chunk_size = chunk_size
        self.d_inner = expand * d_model
        self.n_heads = n_heads
        self.device = device

        # Order: (z, x, B, C, dt)
        d_in_proj = 2 * self.d_inner + 2 * self.d_state + self.n_heads
        self.in_proj = nn.Linear(self.d_model, d_in_proj, bias=False, device=device)

        cond_inner = self.d_inner + 2 * self.d_state
        self.conv1d = nn.Conv1d(
            in_channels=cond_inner,
            out_channels=cond_inner,
            kernel_size=self.d_conv,
            groups=cond_inner,
            padding=self.d_conv-1,
            device=device,
        )

        self.dt_bias = nn.Parameter(torch.empty(self.n_heads, device=device))
        self.A_log = nn.Parameter(torch.empty(self.n_heads, device=device))
        self.D = nn.Parameter(torch.empty(self.n_heads, device=device))
        self.norm = GatedRMSNorm(self.d_inner, device=device)
        self.out_proj = nn.Linear(self.d_inner, self.d_model, bias=False, device=device)
        
        self._reset_parameters()

    def _reset_parameters(self):
        # Xavier/Glorot for Linear layers
        nn.init.xavier_uniform_(self.in_proj.weight)
        nn.init.xavier_uniform_(self.out_proj.weight)

        # Kaiming He Initialization for Conv1D
        nn.init.kaiming_uniform_(self.conv1d.weight, nonlinearity='relu')
        if self.conv1d.bias is not None:
            nn.init.zeros_(self.conv1d.bias)

        # Initialize dt_bias (time-step scaling factor)
        nn.init.uniform_(self.dt_bias, -0.5, 0.5)

        # Initialize A_log with small negative values for stability
        nn.init.uniform_(self.A_log, -0.1, -0.01)

        # Initialize D with small values (identity-like for residual connections)
        nn.init.uniform_(self.D, 0.9, 1.1)

    def forward(self, u):
        """
        Arguments
            u: (batch, seq_len, d_model) input. seq_len should be a multiple of chunk_size.

        Return (y, h)
            y: (batch, seq_len, d_model) output
        """
        # Keep track of original sequence length
        seq_len = u.shape[1]
        u = F.pad(u, (0, 0, 0, self.chunk_size - seq_len % self.chunk_size), value=0.0)
        padded_seq_len = u.shape[1]
        
        A = -torch.exp(self.A_log)
        zxbcdt = self.in_proj(u)
        
        z, xBC, dt = torch.split(
            zxbcdt,
            [
                self.d_inner,
                self.d_inner + 2 * self.d_state,
                self.n_heads,
            ],
            dim=-1,
        )
        
        # Apply convolution
        if cuda_causal_conv1d is not None:
            xBC = cuda_causal_conv1d(
                xBC.transpose(1, 2).contiguous(),
                rearrange(self.conv1d.weight, "d 1 w -> d w"),
                bias=self.conv1d.bias,
                activation="silu",
            ).transpose(1, 2)
        else:
            xBC = F.silu(self.conv1d(xBC.transpose(1, 2).contiguous()).transpose(1, 2)[:, :padded_seq_len])
        
        x, B, C = torch.split(
            xBC,
            [
                self.d_inner,
                self.d_state,
                self.d_state,
            ],
            dim=-1
        )
        
        # Reshape x for the SSM operation
        x = x.reshape(x.shape[0], padded_seq_len, self.n_heads, -1)
        
        dt = F.softplus(dt + self.dt_bias)
        
        y, ssm_state = self.ssd(
            x * dt.unsqueeze(-1),
            A * dt,
            B.unsqueeze(2),
            C.unsqueeze(2),
            self.chunk_size,
        )
        
        y = y + x * self.D.unsqueeze(-1)
        y = y.reshape(y.shape[0], padded_seq_len, -1)
        y = self.norm(y, z)
        y = self.out_proj(y)

        return y[:, :seq_len]

    def segsum(self, x):
        """Stable segment sum calculation.

        `exp(segsum(A))` produces a 1-semiseparable matrix, which is equivalent to a scalar SSM.

        Source: https://github.com/state-spaces/mamba/blob/219f03c840d5a44e7d42e4e728134834fddccf45/mamba_ssm/modules/ssd_minimal.py#L23-L32
        """
        T = x.size(-1)
        x = repeat(x, "... d -> ... d e", e=T)
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=self.device), diagonal=-1)
        x = x.masked_fill(~mask, 0)
        x_segsum = torch.cumsum(x, dim=-2)
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=self.device), diagonal=0)
        x_segsum = x_segsum.masked_fill(~mask, -torch.inf)
        return x_segsum

    def ssd(self, x, A, B, C, chunk_size, initial_states=None):
        """Structed State Space Duality (SSD) - the core of Mamba-2

        This is almost the exact same minimal SSD code from the blog post.

        Arguments
            x: (batch, seq_len, n_heads, d_head)
            A: (batch, seq_len, n_heads)
            B: (batch, seq_len, n_heads, d_state)
            C: (batch, seq_len, n_heads, d_state)

        Return
            y: (batch, seq_len, n_heads, d_head)

        Source
        1. https://tridao.me/blog/2024/mamba2-part3-algorithm/
        2. https://github.com/state-spaces/mamba/blob/219f03c840d5a44e7d42e4e728134834fddccf45/mamba_ssm/modules/ssd_minimal.py#L34-L78
        """
        assert x.shape[1] % chunk_size == 0

        # Rearrange into chunks
        # Step 1, 2 and 4 of SSD can be computed in parallel for each chunk across devices (sequence parallel)
        # This is not implemented and left as an exercise for the reader 😜
        x, A, B, C = [
            rearrange(m, "b (c l) ... -> b c l ...", l=chunk_size) for m in (x, A, B, C)
        ]

        A = rearrange(A, "b c l h -> b h c l")
        A_cumsum = torch.cumsum(A, dim=-1)

        # 1. Compute the output for each intra-chunk (diagonal blocks)
        L = torch.exp(self.segsum(A))
        Y_diag = torch.einsum("bclhn, bcshn, bhcls, bcshp -> bclhp", C, B, L, x)

        # 2. Compute the state for each intra-chunk
        # (right term of low-rank factorization of off-diagonal blocks; B terms)
        decay_states = torch.exp(A_cumsum[:, :, :, -1:] - A_cumsum)
        states = torch.einsum("bclhn, bhcl, bclhp -> bchpn", B, decay_states, x)

        # 3. Compute the inter-chunk SSM recurrence; produces correct SSM states at chunk boundaries
        # (middle term of factorization of off-diag blocks; A terms)
        if initial_states is None:
            initial_states = torch.zeros_like(states[:, :1])
        states = torch.cat([initial_states, states], dim=1)
        decay_chunk = torch.exp(self.segsum(F.pad(A_cumsum[:, :, :, -1], (1, 0))))
        new_states = torch.einsum("bhzc, bchpn -> bzhpn", decay_chunk, states)
        states, final_state = new_states[:, :-1], new_states[:, -1]

        # 4. Compute state -> output conversion per chunk
        # (left term of low-rank factorization of off-diagonal blocks; C terms)
        state_decay_out = torch.exp(A_cumsum)
        Y_off = torch.einsum("bclhn, bchpn, bhcl -> bclhp", C, states, state_decay_out)

        # Add output of intra-chunk and inter-chunk terms (diagonal and off-diagonal blocks)
        Y = rearrange(Y_diag + Y_off, "b c l h p -> b (c l) h p")

        return Y, final_state

class Mamba2(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1,
                 d_state=None, d_conv=4, expand=2,
                 use_embedding=True, weight_tying=False,
                 bidirectional=False,
                 pos_encoding=False, pos_encoding_max_len=None,
                 chunk_size=64, device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.d_state = d_state if d_state is not None else emb_dim
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.bidirectional = bidirectional
        self.use_embedding = use_embedding
        self.device = device

        if use_embedding:
            self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else:
            self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.abs_pos_encoding = None
        if pos_encoding:
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
            self.abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device)
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    mixer=Mamba2Block(
                        d_model=emb_dim,
                        d_state=self.d_state,
                        d_conv=d_conv,
                        expand=expand,
                        n_heads=n_heads,
                        chunk_size=chunk_size,
                        device=device
                    ),
                    norm=GatedRMSNorm(emb_dim, device=device),
                )
            ) for _ in range(n_layers)
        ])
        self.norm_f=GatedRMSNorm(emb_dim, device=device)
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)

    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        if self.abs_pos_encoding is not None:
            pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
            x = x + self.abs_pos_encoding(pos)
        for layer in self.layers:
            x_norm = layer.norm(x)
            y_f = layer.mixer(x_norm)
            y_b = layer.mixer(x_norm.flip(1)) if self.bidirectional else 0.0
            x = x + y_f + y_b
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x[:, :seq_len]

class SeqLinear(nn.Module):
    """
    Linear layer with weights derived from a weighted sum of rank-1 sequential updates.
    """
    def __init__(self, d_model, n_heads,
                 d_conv=4, d_state=None, d_inner=None,
                 chunk_size=64, device="cpu"):
        super().__init__()
        self.d_model = d_model
        self.d_state = d_state if d_state is not None else d_model
        self.d_inner = d_inner if d_inner is not None else d_model
        self.n_heads = n_heads
        self.chunk_size = chunk_size
        self.device = device
        
        d_in_proj = 2 * self.d_state + self.d_inner + self.n_heads
        self.in_proj = nn.Linear(d_model, d_in_proj, bias=False, device=device)
        d_conv_c = 2 * self.d_state + self.d_inner
        self.conv = nn.Conv1d(
            in_channels=d_conv_c,
            out_channels=d_conv_c,
            kernel_size=d_conv,
            groups=d_conv_c,
            padding=d_conv-1,
            device=device,
        )
        self.A = nn.Parameter(torch.empty(n_heads, device=device))
        self.dt_bias = nn.Parameter(torch.empty(n_heads, device=device))
        self.out_proj = nn.Linear(self.d_inner, d_model, bias=False, device=device)
        
        self._reset_parameters()
    
    def _reset_parameters(self):
        nn.init.xavier_uniform_(self.in_proj.weight)
        nn.init.xavier_uniform_(self.out_proj.weight)
        nn.init.xavier_uniform_(self.conv.weight)
        nn.init.uniform_(self.dt_bias, -0.1, 0.1)
        nn.init.uniform_(self.A, -0.01, 0.01)
        
        if self.conv.bias is not None:
            nn.init.constant_(self.conv.bias, 0.)
        if self.in_proj.bias is not None:
            nn.init.constant_(self.in_proj.bias, 0.)
        if self.out_proj.bias is not None:
            nn.init.constant_(self.out_proj.bias, 0.)
    
    def segsum(self, x):
        """Stable segment sum calculation.

        `exp(segsum(A))` produces a 1-semiseparable matrix, which is equivalent to a scalar SSM.

        Source: https://github.com/state-spaces/mamba/blob/219f03c840d5a44e7d42e4e728134834fddccf45/mamba_ssm/modules/ssd_minimal.py#L23-L32
        """
        T = x.size(-1)
        x = repeat(x, "... d -> ... d e", e=T)
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=self.device), diagonal=-1)
        x = x.masked_fill(~mask, 0)
        x_segsum = torch.cumsum(x, dim=-2)
        mask = torch.tril(torch.ones(T, T, dtype=torch.bool, device=self.device), diagonal=0)
        x_segsum = x_segsum.masked_fill(~mask, -torch.inf)
        return x_segsum

    def ssd(self, x, A, B, C, chunk_size, initial_states=None):
        """Structed State Space Duality (SSD) - the core of Mamba-2

        This is almost the exact same minimal SSD code from the blog post.

        Arguments
            x: (batch, seq_len, n_heads, d_head)
            A: (batch, seq_len, n_heads)
            B: (batch, seq_len, n_heads, d_state)
            C: (batch, seq_len, n_heads, d_state)

        Return
            y: (batch, seq_len, n_heads, d_head)

        Source
        1. https://tridao.me/blog/2024/mamba2-part3-algorithm/
        2. https://github.com/state-spaces/mamba/blob/219f03c840d5a44e7d42e4e728134834fddccf45/mamba_ssm/modules/ssd_minimal.py#L34-L78
        """
        # Rearrange into chunks
        # Step 1, 2 and 4 of SSD can be computed in parallel for each chunk across devices (sequence parallel)
        # This is not implemented and left as an exercise for the reader 😜
        x, A, B, C = [
            rearrange(m, "b (c l) ... -> b c l ...", l=chunk_size) for m in (x, A, B, C)
        ]

        A = rearrange(A, "b c l h -> b h c l")
        A_cumsum = torch.cumsum(A, dim=-1)

        # 1. Compute the output for each intra-chunk (diagonal blocks)
        L = torch.exp(self.segsum(A))
        Y_diag = torch.einsum("bclhn, bcshn, bhcls, bcshp -> bclhp", C, B, L, x)

        # 2. Compute the state for each intra-chunk
        # (right term of low-rank factorization of off-diagonal blocks; B terms)
        decay_states = torch.exp(A_cumsum[:, :, :, -1:] - A_cumsum)
        states = torch.einsum("bclhn, bhcl, bclhp -> bchpn", B, decay_states, x)

        # 3. Compute the inter-chunk SSM recurrence; produces correct SSM states at chunk boundaries
        # (middle term of factorization of off-diag blocks; A terms)
        if initial_states is None:
            initial_states = torch.zeros_like(states[:, :1])
        states = torch.cat([initial_states, states], dim=1)
        decay_chunk = torch.exp(self.segsum(F.pad(A_cumsum[:, :, :, -1], (1, 0))))
        new_states = torch.einsum("bhzc, bchpn -> bzhpn", decay_chunk, states)
        states = new_states[:, :-1]

        # 4. Compute state -> output conversion per chunk
        # (left term of low-rank factorization of off-diagonal blocks; C terms)
        state_decay_out = torch.exp(A_cumsum)
        Y_off = torch.einsum("bclhn, bchpn, bhcl -> bclhp", C, states, state_decay_out)

        # Add output of intra-chunk and inter-chunk terms (diagonal and off-diagonal blocks)
        Y = rearrange(Y_diag + Y_off, "b c l h p -> b (c l) h p")

        return Y
    
    def bidirectional(self, x):
        bsz, src_len, d_model = x.size()
        
        if x.size(1) % self.chunk_size != 0:
            x = F.pad(x, (0, 0, 0, self.chunk_size - src_len % self.chunk_size), value=0.0)
        
        x = self.in_proj(x)
        
        x, dt = torch.split(
            x,
            [
                2 * self.d_state + self.d_inner,
                self.n_heads,
            ],
            dim=-1
        )
        
        if cuda_causal_conv1d is not None:
            x_f = cuda_causal_conv1d(
                x.transpose(1, 2).contiguous(),
                self.conv.weight.squeeze(1),
                bias=self.conv.bias,
                activation=None,
            ).transpose(1, 2)
            x_b = cuda_causal_conv1d(
                x.flip(1).transpose(1, 2).contiguous(),
                self.conv.weight.squeeze(1),
                bias=self.conv.bias,
                activation=None,
            ).transpose(1, 2)
        else:
            x_f = self.conv(x.transpose(1, 2).contiguous()).transpose(1, 2)[:, :x.size(1)]
            x_b = self.conv(x.flip(1).transpose(1, 2).contiguous()).transpose(1, 2)[:, :x.size(1)]
        
        C_f, B_f, x_f = torch.split(
            x_f,
            [
                self.d_state,
                self.d_state,
                self.d_inner,
            ],
            dim=-1
        )
        C_b, B_b, x_b = torch.split(
            x_b,
            [
                self.d_state,
                self.d_state,
                self.d_inner,
            ],
            dim=-1
        )
        
        dt = F.softplus(dt + self.dt_bias)
        C_f = rearrange(C_f, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        B_f = rearrange(B_f, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        A_f = self.A * dt
        x_f = rearrange(x_f, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        
        C_b = rearrange(C_b, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        B_b = rearrange(B_b, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        A_b = self.A * dt.flip(1)
        x_b = rearrange(x_b, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        
        norm_f = torch.exp(self.segsum(A_f.transpose(1, 2))).sum(-1).transpose(1, 2).unsqueeze(-1)
        norm_b = torch.exp(self.segsum(A_b.transpose(1, 2))).sum(-1).transpose(1, 2).unsqueeze(-1)

        out_f = self.ssd(x_f, A_f, B_f, C_f, self.chunk_size)[0] / norm_f
        out_b = self.ssd(x_b, A_b, B_b, C_b, self.chunk_size)[0] / norm_b
        
        out = rearrange(out_f + out_b, 'b s h d -> b s (h d)')
        out = self.out_proj(out)
        return out[:, :src_len]
    
    def forward(self, x, mode="causal"):
        if mode == "bidirectional": return self.bidirectional(x)
        bsz, src_len, d_model = x.size()
        
        if mode == "causal" and x.size(1) % self.chunk_size != 0:
            x = F.pad(x, (0, 0, 0, self.chunk_size - src_len % self.chunk_size), value=0.0)
        
        x = self.in_proj(x)
        
        x, dt = torch.split(
            x,
            [
                2 * self.d_state + self.d_inner,
                self.n_heads,
            ],
            dim=-1
        )
        
        if cuda_causal_conv1d is not None:
            x = cuda_causal_conv1d(
                x.transpose(1, 2).contiguous(),
                self.conv.weight.squeeze(1),
                bias=self.conv.bias,
                activation=None,
            ).transpose(1, 2)
        else:
            x = self.conv(x.transpose(1, 2).contiguous()).transpose(1, 2)[:, :x.size(1)]
        
        C, B, x = torch.split(
            x,
            [
                self.d_state,
                self.d_state,
                self.d_inner,
            ],
            dim=-1
        )
        
        dt = F.softplus(dt + self.dt_bias)
        C = rearrange(C, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        B = rearrange(B, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        A = self.A * dt
        x = rearrange(x, 'b s (h d) -> b s h d', h=self.n_heads).contiguous()
        
        if mode == "causal":
            norm = torch.exp(self.segsum(A.transpose(1, 2))).sum(-1).transpose(1, 2).unsqueeze(-1)
            out = self.ssd(x, A, B, C, self.chunk_size)[0] / norm
        elif mode == "noncausal":
            norm = torch.sum(torch.exp(A), dim=1, keepdim=True).unsqueeze(-1)
            out = torch.einsum('bthd, bsh, bshd, bshe -> bthe', C, A, B, x) / norm
        
        out = rearrange(out, 'b s h d -> b s (h d)')
        out = self.out_proj(out)
        return out[:, :src_len]

class SeqMLP(nn.Module):
    def __init__(self, emb_dim, input_dim, output_dim,
                 n_layers=1, n_heads=1, dropout=0.0,
                 d_state=None, d_inner=None, d_conv=4,
                 pos_encoding=False, pos_encoding_max_len=None,
                 use_embedding=True, weight_tying=False, chunk_size=64,
                 mode="causal", device="cpu"):
        super().__init__()
        self.emb_dim = emb_dim
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.n_layers = n_layers
        self.n_heads = n_heads
        self.mode = mode
        self.use_embedding = use_embedding
        self.device = device

        if use_embedding:
            self.embedding = nn.Embedding(input_dim, emb_dim, device=device)
        else:
            self.embedding = nn.Linear(input_dim, emb_dim, bias=False, device=device)
        
        self.abs_pos_encoding = None
        if pos_encoding:
            assert pos_encoding_max_len is not None, "pos_encoding_max_len must be provided for absolute positional encoding"
            self.pos_encoding_max_len = pos_encoding_max_len
            self.abs_pos_encoding = nn.Embedding(pos_encoding_max_len, emb_dim, device=device)
        
        self.layers = nn.ModuleList([
            nn.ModuleDict(
                dict(
                    mixer=SeqLinear(
                        d_model=emb_dim,
                        n_heads=n_heads,
                        d_state=d_state,
                        d_inner=d_inner,
                        d_conv=d_conv,
                        chunk_size=chunk_size,
                        device=device
                    ),
                    dropout = nn.Dropout(dropout),
                    norm=nn.RMSNorm(emb_dim, device=device),
                )
            ) for _ in range(n_layers)
        ])
        self.norm_f=nn.RMSNorm(emb_dim, device=device)
        self.out_proj = nn.Linear(emb_dim, output_dim, bias=False, device=device)
        
        nn.init.xavier_uniform_(self.embedding.weight)
        if weight_tying: self.out_proj.weight = self.embedding.weight
        else: nn.init.xavier_uniform_(self.out_proj.weight)
        
        self.to(device)

    def forward(self, x):
        seq_len = x.size(1)
        if self.use_embedding: x = self.embedding(x.long())
        else: x = self.embedding(x)
        if self.abs_pos_encoding is not None:
            pos = torch.arange(seq_len, device=x.device, dtype=torch.long).unsqueeze(0).expand(x.size(0), -1)
            x = x + self.abs_pos_encoding(pos)
        for layer in self.layers:
            x_norm = layer.norm(x)
            y = layer.dropout(layer.mixer(x_norm, mode=self.mode))
            x = x + y
        x = self.norm_f(x)
        x = self.out_proj(x)
        return x