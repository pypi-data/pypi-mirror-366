#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <list>
#include <map>
#include <stdexcept>
#include <vector>

namespace py = pybind11;

class Bin {
  public:
    double remaining_space;
    size_t bin_index;
    std::vector<int> items;

    Bin(double space, size_t index)
        : remaining_space(space), bin_index(index) {}
};

std::vector<std::vector<int>> bfd(const std::vector<double> &lengths,
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

    std::map<double, std::list<size_t>> bins_map;
    std::vector<Bin> bins;

    for (const auto &pair : length_pairs) {
        double size = pair.first;
        int orig_idx = pair.second;

        auto it = bins_map.lower_bound(size);
        if (it != bins_map.end()) {
            size_t bin_idx = it->second.front();
            it->second.pop_front();
            if (it->second.empty()) {
                bins_map.erase(it);
            }

            Bin &bin = bins[bin_idx];
            bin.remaining_space -= size;
            bin.items.push_back(orig_idx);

            bins_map[bin.remaining_space].push_back(bin_idx);
        } else {
            Bin new_bin(batch_max_length - size, bins.size());
            new_bin.items.push_back(orig_idx);
            bins.push_back(new_bin);
            bins_map[new_bin.remaining_space].push_back(new_bin.bin_index);
        }
    }

    std::vector<std::vector<int>> final_result;
    for (const auto &bin : bins) {
        final_result.push_back(bin.items);
    }

    return final_result;
}

PYBIND11_MODULE(bfd, m) {
    m.doc() =
        "BFD (Best Fit Decreasing) algorithm optimized implementation in C++";
    m.def("bfd", &bfd, "Optimized BFD algorithm");
}
