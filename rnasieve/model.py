import numpy as np
import matplotlib.pyplot as plt
from rnasieve.algo import find_mixtures


class RNASieveModel:
    def __init__(self, observed_phi, observed_sigma, observed_m, labels=None):
        assert observed_phi.shape == observed_sigma.shape, 'Reference mean matrix and variance matrix must have the same dimensions'
        assert observed_m.shape[1] == observed_phi.shape[1], 'Number of cell types must be consistent with reference matrix'
        assert labels is None or len(
            labels) == observed_phi.shape[1], 'Labels must match reference matrix dimension'

        self.observed_phi = observed_phi
        self.observed_sigma = observed_sigma
        self.observed_m = observed_m
        self.labels = labels if labels is not None else list(
            range(self.observed_phi.shape[1]))

    def predict(self, psis, labels=None):
        assert psis.shape[0] == self.observed_phi.shape[0], 'Bulks must have the same number of genes as the reference matrix'
        assert labels is None or len(
            labels) == psis.shape[1], 'Labels must match bulk matrix dimension'

        labels = labels if labels is not None else list(range(psis.shape[1]))
        non_zero_idxs = np.where(psis.any(axis=1))
        alpha_LS, n_hats, phi_hat = find_mixtures(
            self.observed_phi[non_zero_idxs], self.observed_sigma[non_zero_idxs], self.observed_m, psis[non_zero_idxs])
        return RNASieveResults(self.observed_phi[non_zero_idxs], self.observed_sigma[non_zero_idxs],
                               self.observed_m, self.labels, psis[non_zero_idxs], labels, alpha_LS, n_hats, phi_hat)


class RNASieveResults:
    def __init__(self, observed_phi, observed_sigma, observed_m,
                 cell_type_labels, psis, bulk_labels, alpha_hats, n_hats, phi_hat):
        self.observed_phi = observed_phi
        self.observed_sigma = observed_sigma
        self.observed_m = observed_m
        self.cell_type_labels = cell_type_labels
        self.psis = psis
        self.bulk_labels = bulk_labels
        self.alpha_hats = alpha_hats
        self.n_hats = n_hats
        self.phi_hat = phi_hat

    def plot_proportions(self, ax, plot_type="bar"):
        plt.style.use('ggplot')
        colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

        if plot_type == "bar":
            bars = []
            bar_width = 0.8 / self.alpha_hats.shape[1]

            for i in range(self.alpha_hats.shape[1]):
                x_offset = (
                    i - self.alpha_hats.shape[1] / 2) * bar_width + bar_width / 2
                for x, y in enumerate(self.alpha_hats[:, i]):
                    bar = ax.bar(x + x_offset, y, width=bar_width *
                                 0.9, color=colors[i % len(colors)])
                bars.append(bar[0])

            ax.set_ylabel("Proportion of bulk")
            ax.set_ylim((0, 1))
            ax.set_xlabel("Bulk label")
            ax.set_xticks(range(self.alpha_hats.shape[0]))
            ax.set_xticklabels(self.bulk_labels)
            ax.grid()
            ax.legend(bars, self.cell_type_labels, bbox_to_anchor=(-.15, 1))

        if plot_type == "scatter":
            assert isinstance(self.bulk_labels[0], int) or isinstance(
                self.bulk_labels[0], float), 'Bulk labels must be quantitative'

            for i in range(self.alpha_hats.shape[1]):
                ax.scatter(self.bulk_labels, self.alpha_hats[:, i], color=colors[i % len(
                    colors)], label=self.cell_type_labels[i])

            ax.set_ylabel("Proportion of bulk")
            ax.set_ylim((0, 1))
            ax.set_xlabel("Bulk Metric")
            ax.grid()
            ax.legend(bbox_to_anchor=(-.15, 1))

        if plot_type == "stacked":
            bottoms = np.zeros(self.alpha_hats.shape[0])
            for i in range(self.alpha_hats.shape[1]):
                ax.bar(np.arange(len(self.bulk_labels)),
                       self.alpha_hats[:, i], bottom=bottoms, edgecolor='white', width=1, label=self.cell_type_labels[i])
                bottoms += self.alpha_hats[:, i]

            ax.set_ylabel("Proportion of bulk")
            ax.set_ylim((0, 1))
            ax.set_xlabel("Bulk label")
            ax.set_xticks(range(self.alpha_hats.shape[0]))
            ax.set_xticklabels(self.bulk_labels)
            ax.grid()
            ax.legend(bbox_to_anchor=(-.15, 1))

        return ax
