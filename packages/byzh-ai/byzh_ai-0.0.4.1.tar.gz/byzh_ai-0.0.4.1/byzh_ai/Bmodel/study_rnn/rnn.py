import torch
import torch.nn as nn
import torch.nn.functional as F


class OneLayer_RNN(nn.Module):
    '''
    input_size: C
    seq_len: L
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size):
        super().__init__()
        self.input_size = input_size
        self.hidden_size = hidden_size

        self.W_ih = nn.Parameter(torch.randn(hidden_size, input_size)) # [H, C]
        self.W_hh = nn.Parameter(torch.randn(hidden_size, hidden_size)) # [H, H]
        self.b = nn.Parameter(torch.zeros(hidden_size)) # [H]

    def forward(self, x, h0=None):
        # x: [L, B, C]
        seq_len, batch_size, input_size = x.shape

        # h: [B, H]
        if h0 is None:
            h_t = torch.zeros(batch_size, self.hidden_size, device=x.device)
        else:
            h_t = h0

        outputs = []
        for t in range(seq_len):
            x_t = x[t] # [B, C]
            h_t = torch.tanh(x_t @ self.W_ih.T + h_t @ self.W_hh.T + self.b) # self.b会被广播成[B, H]
            outputs.append(h_t)

        return torch.stack(outputs, dim=0), h_t # [L, B, H], [B, H]


class Layers_RNN(nn.Module):
    '''
    input_size: C
    seq_len: L
    hidden_size: H
    num_layers: N
    '''
    def __init__(self, input_size, hidden_size, num_layers=1, batch_first=False):
        '''
        如果batch_first=False, 输入的x的形状为[L, B, C]

        如果batch_first=True, 输入的x的形状为[B, L, C]
        '''
        super().__init__()
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        self.batch_first = batch_first


        self.W_ih_list = nn.ModuleList() # [C, H], [H, H], [H, H], ...
        self.W_hh_list = nn.ModuleList() # [H, H], [H, H], [H, H], ...
        self.b_list = nn.ParameterList() # H, H, H, ......

        for layer in range(num_layers):
            in_size = input_size if layer == 0 else hidden_size # C, H, H, ......
            self.W_ih_list.append(nn.Linear(in_size, hidden_size, bias=False))
            self.W_hh_list.append(nn.Linear(hidden_size, hidden_size, bias=False))
            self.b_list.append(nn.Parameter(torch.zeros(hidden_size)))

    def forward(self, x, h0=None):
        '''

        :param x:
        :param h0: [L, B, H]
        :return: x, h <-> [L, B, H], [L, B, H]
        '''
        if self.batch_first:
            x = x.transpose(0, 1) # [B, L, C] -> [L, B, C]

        # x: [L, B, C]
        seq_len, batch_size, input_size = x.size()

        # h_t: [B, H] * layers
        if h0 is None:
            h_t = [torch.zeros(batch_size, self.hidden_size, device=x.device) for _ in range(self.num_layers)]
        else:
            # torch.unbind用于 沿着指定维度 将张量分割成一系列的子张量
            h_t = list(torch.unbind(h0, dim=0))  # shape: [num_layers, batch, hidden_size]

        layer_input = x # 第一次为[B, C], 后续变为[B, H]
        for layer in range(self.num_layers):
            outputs = []
            h = h_t[layer] # [B, H]
            for t in range(seq_len):
                x_t = layer_input[t] # [B, C]
                h = torch.tanh(
                    self.W_ih_list[layer](x_t)
                    + self.W_hh_list[layer](h)
                    + self.b_list[layer]
                )
                outputs.append(h)
            layer_input = torch.stack(outputs, dim=0)
            h_t[layer] = h

        h_n = torch.stack(h_t, dim=0)  # [num_layers, batch, hidden_size]

        if self.batch_first:
            layer_input = layer_input.transpose(0, 1) # [L, B, H] -> [B, L, H]
        return layer_input, h_n


if __name__ == '__main__':
    seq_len, batch_size, input_size, hidden_size, num_layers = 7, 4, 8, 16, 3
    x = torch.randn(seq_len, batch_size, input_size)

    # OneLayer_RNN
    rnn = OneLayer_RNN(input_size, hidden_size)
    rnn_out, h_n = rnn(x)
    print("OneLayer_RNN output:", rnn_out.shape)  # [seq_len, batch, hidden_size]

    # Layers_RNN
    rnn = Layers_RNN(input_size, hidden_size, num_layers)
    out_rnn, h_n_rnn = rnn(x)
    print("Layers_RNN output:", out_rnn.shape)  # [seq_len, batch, hidden_size]