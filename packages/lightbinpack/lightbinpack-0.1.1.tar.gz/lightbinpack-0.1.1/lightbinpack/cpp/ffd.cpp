#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

class SegmentTree {
  public:
    SegmentTree(size_t size) : size(size) { tree.resize(4 * size, 0.0); }

    void build(const std::vector<double> &bins_remaining_space) {
        build(1, 0, size - 1, bins_remaining_space);
    }

    int query(double size_needed) {
        return query(1, 0, this->size - 1, size_needed);
    }

    void update(int idx, double value) { update(1, 0, size - 1, idx, value); }

  private:
    size_t size;
    std::vector<double> tree;

    void build(int node, int start, int end,
               const std::vector<double> &bins_remaining_space) {
        if (start == end) {
            tree[node] = bins_remaining_space[start];
        } else {
            int mid = (start + end) / 2;
            build(2 * node, start, mid, bins_remaining_space);
            build(2 * node + 1, mid + 1, end, bins_remaining_space);
            tree[node] = std::max(tree[2 * node], tree[2 * node + 1]);
        }
    }

    int query(int node, int start, int end, double size_needed) {
        if (tree[node] < size_needed) {
            return -1;
        }
        if (start == end) {
            return start;
        }
        int mid = (start + end) / 2;
        int left_result = query(2 * node, start, mid, size_needed);
        if (left_result != -1) {
            return left_result;
        }
        return query(2 * node + 1, mid + 1, end, size_needed);
    }

    void update(int node, int start, int end, int idx, double value) {
        if (start == end) {
            tree[node] = value;
        } else {
            int mid = (start + end) / 2;
            if (idx <= mid) {
                update(2 * node, start, mid, idx, value);
            } else {
                update(2 * node + 1, mid + 1, end, idx, value);
            }
            tree[node] = std::max(tree[2 * node], tree[2 * node + 1]);
        }
    }
};

std::vector<std::vector<int>> ffd(const std::vector<double> &lengths,
                                  double batch_max_length) {
    if (lengths.empty() || batch_max_length <= 0) {
        return {};
    }

    std::vector<std::pair<double, int>> length_pairs;
    length_pairs.reserve(lengths.size());
    for (size_t i = 0; i < lengths.size(); i++) {
        if (lengths[i] > batch_max_length) {
            throw std::runtime_error("Item size exceeds batch max length");
        }
        length_pairs.emplace_back(lengths[i], i);
    }

    std::sort(length_pairs.begin(), length_pairs.end(),
              std::greater<std::pair<double, int>>());

    size_t n = lengths.size();
    std::vector<double> bins_remaining_space(n, 0.0);
    std::vector<std::vector<int>> bins_items(n);

    SegmentTree segment_tree(n);
    segment_tree.build(bins_remaining_space);

    size_t bin_count = 0;

    for (const auto &pair : length_pairs) {
        double size = pair.first;
        int orig_idx = pair.second;

        int bin_idx = segment_tree.query(size);

        if (bin_idx != -1 && bin_idx < static_cast<int>(bin_count)) {
            bins_remaining_space[bin_idx] -= size;
            bins_items[bin_idx].push_back(orig_idx);
            segment_tree.update(bin_idx, bins_remaining_space[bin_idx]);
        } else {
            bins_remaining_space[bin_count] = batch_max_length - size;
            bins_items[bin_count].push_back(orig_idx);
            segment_tree.update(bin_count, bins_remaining_space[bin_count]);
            bin_count++;
        }
    }

    bins_items.resize(bin_count);

    return bins_items;
}

PYBIND11_MODULE(ffd, m) {
    m.doc() = "FFD (First Fit Decreasing) algorithm implementation in C++";
    m.def("ffd", &ffd, "FFD algorithm");
}
