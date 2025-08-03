#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <queue>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

class IterativeSegmentTree {
  private:
    int n;
    std::vector<int> tree;

  public:
    IterativeSegmentTree(int max_length) {
        n = 1;
        while (n < max_length + 1)
            n <<= 1;
        tree.assign(2 * n, 0);
        tree[n - 1 + max_length] = max_length;
        for (int i = max_length - 1; i >= 0; --i) {
            tree[n - 1 + i] = 0;
        }
        for (int i = n - 2; i >= 0; --i) {
            tree[i] = std::max(tree[2 * i + 1], tree[2 * i + 2]);
        }
    }

    void update(int idx, int val) {
        idx += n - 1;
        tree[idx] = val;
        while (idx > 0) {
            idx = (idx - 1) / 2;
            int left = tree[2 * idx + 1];
            int right = tree[2 * idx + 2];
            int new_val = std::max(left, right);
            if (tree[idx] == new_val)
                break;
            tree[idx] = new_val;
        }
    }

    int find_best_fit(int target) const {
        int idx = 0;
        if (tree[idx] < target)
            return -1;
        while (idx < (n - 1)) {
            if (tree[2 * idx + 1] >= target)
                idx = 2 * idx + 1;
            else
                idx = 2 * idx + 2;
        }
        int capacity = idx - (n - 1);
        return tree[idx] >= target ? capacity : -1;
    }
};

class HeterogeneousBinGroup {
  private:
    std::vector<std::vector<int>> bins;
    std::vector<int> remaining_space;
    std::vector<int> bin_lengths;
    std::vector<long long> sum_of_squares;

  public:
    HeterogeneousBinGroup(const std::vector<int> &batch_max_lengths) {
        bins.resize(batch_max_lengths.size());
        remaining_space = batch_max_lengths;
        bin_lengths = batch_max_lengths;
        sum_of_squares.resize(batch_max_lengths.size(), 0);
    }

    bool can_fit(int size) const {
        for (int i = 0; i < (int)remaining_space.size(); ++i) {
            if (remaining_space[i] >= size) {
                return true;
            }
        }
        return false;
    }

    int get_max_remaining() const {
        int max_val = 0;
        for (auto space : remaining_space) {
            if (space > max_val)
                max_val = space;
        }
        return max_val;
    }

    void add_item(int item_idx, int size, long long weight) {
        int chosen_bin = -1;
        double min_ratio = std::numeric_limits<double>::infinity();

        for (int i = 0; i < (int)bins.size(); ++i) {
            if (remaining_space[i] >= size) {
                double ratio =
                    (double)sum_of_squares[i] / (double)bin_lengths[i];
                if (ratio < min_ratio) {
                    min_ratio = ratio;
                    chosen_bin = i;
                }
            }
        }

        if (chosen_bin == -1) {
            throw std::runtime_error("No suitable bin found in the group");
        }

        bins[chosen_bin].push_back(item_idx);
        remaining_space[chosen_bin] -= size;
        sum_of_squares[chosen_bin] += weight;
    }

    const std::vector<std::vector<int>> &get_bins() const { return bins; }
};

std::vector<std::vector<std::vector<int>>>
ohgbfd(const std::vector<int> &lengths,
       const std::vector<int> &batch_max_lengths, int item_max_length = -1,
       const std::vector<long long> &weights = std::vector<long long>()) {
    if (lengths.empty() || batch_max_lengths.empty()) {
        return {};
    }

    // Validate weights if provided
    if (!weights.empty() && weights.size() != lengths.size()) {
        throw std::runtime_error(
            "Weights vector must have the same size as lengths vector");
    }

    int max_batch_length = 0;
    for (int length : batch_max_lengths) {
        if (length <= 0) {
            throw std::runtime_error("Bin length must be positive");
        }
        max_batch_length = std::max(max_batch_length, length);
    }

    if (item_max_length <= 0) {
        item_max_length = 0;
        for (int length : lengths) {
            item_max_length = std::max(item_max_length, length);
        }
    }

    std::vector<std::vector<std::pair<int, long long>>> count(item_max_length +
                                                              1);
    count.reserve(item_max_length + 1);
    for (size_t i = 0; i < lengths.size(); ++i) {
        int len = lengths[i];
        if (len > max_batch_length) {
            throw std::runtime_error("Item size exceeds maximum bin length");
        }
        if (len > item_max_length) {
            throw std::runtime_error("Item size exceeds item max length");
        }
        if (len <= 0) {
            throw std::runtime_error("Item size must be positive");
        }
        long long weight = weights.empty() ? (long long)len * len : weights[i];
        count[len].emplace_back(i, weight);
    }

    IterativeSegmentTree seg_tree(max_batch_length);

    std::vector<std::vector<size_t>> capacity_to_groups(max_batch_length + 1);
    std::vector<HeterogeneousBinGroup> groups;
    groups.reserve(lengths.size() / (2 * batch_max_lengths.size()) + 1);

    groups.emplace_back(batch_max_lengths);
    capacity_to_groups[groups.back().get_max_remaining()].push_back(0);
    seg_tree.update(groups.back().get_max_remaining(),
                    groups.back().get_max_remaining());

    std::vector<std::vector<std::vector<int>>> result;
    result.reserve(lengths.size() / (2 * batch_max_lengths.size()) + 1);

    for (int size = item_max_length; size >= 1; --size) {
        for (const auto &[orig_idx, weight] : count[size]) {
            int best_capacity = seg_tree.find_best_fit(size);

            if (best_capacity != -1) {
                size_t group_idx = capacity_to_groups[best_capacity].back();
                capacity_to_groups[best_capacity].pop_back();
                if (capacity_to_groups[best_capacity].empty()) {
                    seg_tree.update(best_capacity, 0);
                }

                groups[group_idx].add_item(orig_idx, size, weight);
                int new_capacity = groups[group_idx].get_max_remaining();

                capacity_to_groups[new_capacity].push_back(group_idx);
                if (new_capacity > 0) {
                    seg_tree.update(new_capacity, new_capacity);
                }
            } else {
                size_t new_group_idx = groups.size();
                groups.emplace_back(batch_max_lengths);
                groups.back().add_item(orig_idx, size, weight);

                int new_capacity = groups.back().get_max_remaining();
                capacity_to_groups[new_capacity].push_back(new_group_idx);
                seg_tree.update(new_capacity, new_capacity);
            }
        }
    }

    result.reserve(groups.size());
    for (const auto &group : groups) {
        result.push_back(group.get_bins());
    }

    if (result.size() >= 2) {
        auto &target_group = result.back();
        const auto &source_group = result.front();

        std::vector<size_t> empty_bin_indices;
        for (size_t bin_idx = 0; bin_idx < target_group.size(); ++bin_idx) {
            if (target_group[bin_idx].empty()) {
                empty_bin_indices.push_back(bin_idx);
            }
        }

        bool fallback_to_repeat = false;
        if (!empty_bin_indices.empty()) {
            bool early_termination = false;
            for (int group_idx = result.size() - 2;
                 group_idx >= 0 && !empty_bin_indices.empty() &&
                 !early_termination;
                 --group_idx) {
                for (int bin_idx = result[group_idx].size() - 1;
                     bin_idx >= 0 && !empty_bin_indices.empty() &&
                     !early_termination;
                     --bin_idx) {
                    auto &donor_bin = result[group_idx][bin_idx];
                    if (donor_bin.size() >= 2) {
                        int item = donor_bin.back();
                        donor_bin.pop_back();

                        size_t target_bin_idx = empty_bin_indices.back();
                        empty_bin_indices.pop_back();
                        target_group[target_bin_idx].push_back(item);
                    } else if (donor_bin.size() <= 1) {
                        early_termination = true;
                    }
                }
            }

            if (!empty_bin_indices.empty()) {
                fallback_to_repeat = true;
            }
        }

        if (fallback_to_repeat) {
            int source_bin_idx = 0;
            for (size_t target_bin_idx = 0;
                 target_bin_idx < target_group.size(); ++target_bin_idx) {
                if (target_group[target_bin_idx].empty() &&
                    source_bin_idx < source_group.size()) {
                    target_group[target_bin_idx] =
                        source_group[source_bin_idx++];
                }
            }
        }
    }

    return result;
}

PYBIND11_MODULE(ohgbfd, m) {
    m.doc() =
        "Optimized Heterogeneous Grouped BFD (Best Fit Decreasing) algorithm "
        "implementation";
    m.def("ohgbfd", &ohgbfd, "Optimized Heterogeneous Grouped BFD algorithm",
          py::arg("lengths"), py::arg("batch_max_lengths"),
          py::arg("item_max_length") = -1,
          py::arg("weights") = std::vector<long long>());
}
