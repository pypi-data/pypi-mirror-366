#include <omp.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
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

std::vector<std::vector<int>> obfd_worker(const std::vector<int> &lengths,
                                          const std::vector<int> &indices,
                                          int batch_max_length,
                                          int item_max_length) {
    if (indices.empty()) {
        return {};
    }

    std::vector<std::vector<int>> count(item_max_length + 1);
    for (int idx : indices) {
        int len = lengths[idx];
        count[len].push_back(idx);
    }

    IterativeSegmentTree seg_tree(batch_max_length);
    std::vector<std::vector<size_t>> capacity_to_bins(batch_max_length + 1);
    std::vector<size_t> bins_remaining;
    std::vector<std::vector<int>> bins_items;

    bins_remaining.push_back(batch_max_length);
    capacity_to_bins[batch_max_length].push_back(0);
    seg_tree.update(batch_max_length, batch_max_length);
    bins_items.emplace_back();

    for (int size = item_max_length; size >= 1; --size) {
        for (int orig_idx : count[size]) {
            int best_capacity = seg_tree.find_best_fit(size);

            if (best_capacity != -1) {
                size_t bin_idx = capacity_to_bins[best_capacity].back();
                capacity_to_bins[best_capacity].pop_back();
                if (capacity_to_bins[best_capacity].empty()) {
                    seg_tree.update(best_capacity, 0);
                }

                int new_capacity = bins_remaining[bin_idx] - size;
                bins_remaining[bin_idx] = new_capacity;
                bins_items[bin_idx].push_back(orig_idx);

                capacity_to_bins[new_capacity].push_back(bin_idx);
                if (new_capacity > 0) {
                    seg_tree.update(new_capacity, new_capacity);
                }
            } else {
                size_t new_bin_idx = bins_remaining.size();
                bins_remaining.push_back(batch_max_length - size);
                bins_items.emplace_back();
                bins_items.back().push_back(orig_idx);

                int new_capacity = batch_max_length - size;
                capacity_to_bins[new_capacity].push_back(new_bin_idx);
                seg_tree.update(new_capacity, new_capacity);
            }
        }
    }

    return bins_items;
}

std::vector<std::vector<int>> obfdp(const std::vector<int> &lengths,
                                    int batch_max_length,
                                    int item_max_length = -1) {
    if (lengths.empty() || batch_max_length <= 0) {
        return {};
    }

    if (item_max_length <= 0) {
        item_max_length = 0;
        for (int length : lengths) {
            item_max_length = std::max(item_max_length, length);
        }
    }

    for (int len : lengths) {
        if (len > batch_max_length) {
            throw std::runtime_error("Item size exceeds batch max length");
        }
        if (len > item_max_length) {
            throw std::runtime_error("Item size exceeds item max length");
        }
        if (len <= 0) {
            throw std::runtime_error("Item size must be positive");
        }
    }

    int num_threads = 1;
    if (lengths.size() > 20000)
        num_threads = 2;
    if (lengths.size() > 100000)
        num_threads = 4;
    if (lengths.size() > 500000)
        num_threads = omp_get_max_threads();

    std::vector<std::vector<int>> groups(num_threads);
    for (size_t i = 0; i < lengths.size(); ++i) {
        groups[i % num_threads].push_back(i);
    }

    std::vector<std::vector<std::vector<int>>> parallel_results(num_threads);
#pragma omp parallel for num_threads(num_threads)
    for (int i = 0; i < num_threads; ++i) {
        parallel_results[i] =
            obfd_worker(lengths, groups[i], batch_max_length, item_max_length);
    }

    std::vector<int> repack_items;
    std::vector<std::vector<int>> final_bins;

    for (const auto &group_result : parallel_results) {
        if (!group_result.empty()) {
            final_bins.insert(final_bins.end(), group_result.begin(),
                              group_result.end() - 1);
            const auto &last_bin = group_result.back();
            repack_items.insert(repack_items.end(), last_bin.begin(),
                                last_bin.end());
        }
    }

    if (!repack_items.empty()) {
        auto repacked = obfd_worker(lengths, repack_items, batch_max_length,
                                    item_max_length);
        final_bins.insert(final_bins.end(), repacked.begin(), repacked.end());
    }

    return final_bins;
}

PYBIND11_MODULE(obfdp, m) {
    m.doc() = "Parallel Optimized BFD (Best Fit Decreasing) algorithm "
              "implementation";
    m.def("obfdp", &obfdp, "Parallel Optimized BFD algorithm",
          py::arg("lengths"), py::arg("batch_max_length"),
          py::arg("item_max_length") = -1);
}
