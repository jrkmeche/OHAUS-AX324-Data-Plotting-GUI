import plotly.graph_objects as go

class DerivativePlotter:
    def __init__(self, df, epsilon=1e-4):
        self.df = df
        self.epsilon = epsilon

    def build_plot(self):
        fig = go.Figure()

        for file_name in self.df['SourceFile'].unique():
            df_subset = self.df[self.df['SourceFile'] == file_name].copy()
            df_subset = df_subset.reset_index(drop=True)
            df_subset['AlignedTime'] = df_subset.index * 1

            fig.add_trace(go.Scatter(
                x=df_subset['AlignedTime'],
                y=df_subset['Weight'],
                mode='lines',
                name=f'{file_name}'
            ))
            
            
            #derivative stuff, need to fix
            #derivative = df_subset['Weight'].diff()
            #zero_indices = derivative[derivative.abs() < self.epsilon].index
            #x_zero = df_subset['AlignedTime'].loc[zero_indices]
            #y_zero = df_subset['Weight'].loc[zero_indices]

            #fig.add_trace(go.Scatter(
            #    x=x_zero,
            #    y=y_zero,
            #    mode='markers',
            #    name=f'{file_name} Zero Deriv',
            #    marker=dict(color='red', size=8, symbol='circle')
            #))

        fig.update_layout(title='Scale Plots (All Start at t=0)',
                          xaxis_title='Time (s)', yaxis_title='Weight (g)')
        return fig