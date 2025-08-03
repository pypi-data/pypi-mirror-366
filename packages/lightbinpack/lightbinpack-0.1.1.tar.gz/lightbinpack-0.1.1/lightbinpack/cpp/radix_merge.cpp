#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cstdint>
#include <functional>
#include <memory>
#include <set>
#include <string>
#include <tuple>
#include <unordered_map>
#include <vector>

namespace py = pybind11;

inline bool has_min_prefix_match(const std::vector<int> &list1,
                                 const std::vector<int> &list2,
                                 int min_prefix_match) {
    int match_length = 0;
    int min_size = std::min(static_cast<int>(list1.size()),
                            static_cast<int>(list2.size()));

    while (match_length < min_size && match_length < min_prefix_match) {
        if (list1[match_length] != list2[match_length]) {
            return false;
        }
        match_length++;
    }

    return match_length >= min_prefix_match;
}

inline int max_shared_prefix(const std::vector<int> &list1,
                             const std::vector<int> &list2) {
    int match_length = 0;
    int min_size = std::min(static_cast<int>(list1.size()),
                            static_cast<int>(list2.size()));

    while (match_length < min_size &&
           list1[match_length] == list2[match_length]) {
        match_length++;
    }

    return match_length;
}

struct TrieNode {
    int value;
    uint64_t index_mask;
    std::unordered_map<int, std::unique_ptr<TrieNode>> children;

    TrieNode(int val = -1) : value(val), index_mask(0) {}
};

class IncrementalFlatten {
  public:
    IncrementalFlatten() : total_weight(0) {
        root = std::make_unique<TrieNode>();
    }

    void insert_list(const std::vector<int> &list, size_t list_idx) {
        TrieNode *current = root.get();
        int match_length = 0;
        bool first_mismatch = true;

        for (const int &elem : list) {
            if (current->children.find(elem) == current->children.end()) {
                if (first_mismatch) {
                    first_mismatch = false;
                    total_weight +=
                        list.size() * list.size() - match_length * match_length;
                }
                current->children[elem] = std::make_unique<TrieNode>(elem);
            }
            current = current->children[elem].get();
            current->index_mask |= (1ULL << list_idx);
            if (first_mismatch) {
                match_length++;
            }
        }
    }

    void update_flattened() {
        flattened.clear();
        indices.clear();
        dfs(root.get());
    }

    const std::vector<int> &get_flattened() const { return flattened; }

    const std::vector<uint64_t> &get_indices() const { return indices; }

    int get_total_weight() const { return total_weight; }

  private:
    std::unique_ptr<TrieNode> root;
    std::vector<int> flattened;
    std::vector<uint64_t> indices;
    int total_weight;

    void dfs(TrieNode *node) {
        for (const auto &[key, child] : node->children) {
            flattened.push_back(child->value);
            indices.push_back(child->index_mask);
            dfs(child.get());
        }
    }
};

std::tuple<std::vector<std::vector<std::vector<int>>>, std::vector<int>,
           std::vector<int>, std::vector<std::vector<int>>,
           std::vector<std::vector<uint64_t>>>
radix_merge(const std::vector<std::vector<std::vector<int>>> &input_data,
            int min_prefix_match, int max_length, int max_count,
            bool allow_cross_group_merge) {
    if (input_data.empty()) {
        return std::make_tuple(std::vector<std::vector<std::vector<int>>>(),
                               std::vector<int>(), std::vector<int>(),
                               std::vector<std::vector<int>>(),
                               std::vector<std::vector<uint64_t>>());
    }

    std::vector<std::vector<std::vector<int>>> result;
    std::vector<int> total_lengths;
    std::vector<int> total_weights;
    std::vector<std::vector<int>> flattened_lists;
    std::vector<std::vector<uint64_t>> index_lists;

    if (allow_cross_group_merge) {
        std::vector<int> input_data_lengths;
        input_data_lengths.reserve(input_data.size());
        for (const auto &group : input_data) {
            int total_length = 0;
            for (const auto &list : group) {
                total_length += static_cast<int>(list.size());
            }
            input_data_lengths.push_back(total_length);
        }

        std::vector<std::vector<int>> current_group = input_data[0];
        int current_count = static_cast<int>(input_data[0].size());

        IncrementalFlatten flattener;
        for (size_t list_idx = 0; list_idx < current_group.size(); ++list_idx) {
            flattener.insert_list(current_group[list_idx], list_idx);
        }
        flattener.update_flattened();
        std::vector<int> current_flattened = flattener.get_flattened();
        std::vector<uint64_t> current_indices = flattener.get_indices();
        int current_total_length = static_cast<int>(current_flattened.size());

        for (size_t i = 1; i < input_data.size(); ++i) {
            bool can_merge = false;
            for (const auto &existing_list : current_group) {
                for (const auto &next_list : input_data[i]) {
                    if (has_min_prefix_match(existing_list, next_list,
                                             min_prefix_match)) {
                        can_merge = true;
                        break;
                    }
                }
                if (can_merge)
                    break;
            }

            if (can_merge &&
                (current_count + static_cast<int>(input_data[i].size()) <=
                 max_count)) {
                std::vector<std::vector<int>> temp_group = current_group;
                temp_group.insert(temp_group.end(), input_data[i].begin(),
                                  input_data[i].end());

                size_t original_size = flattener.get_flattened().size();
                for (size_t list_idx = 0; list_idx < input_data[i].size();
                     ++list_idx) {
                    flattener.insert_list(input_data[i][list_idx],
                                          current_group.size() + list_idx);
                }
                flattener.update_flattened();
                std::vector<int> temp_flattened = flattener.get_flattened();
                std::vector<uint64_t> temp_indices = flattener.get_indices();
                int temp_total_length = static_cast<int>(temp_flattened.size());

                if (temp_total_length <= max_length) {
                    current_group = std::move(temp_group);
                    current_flattened = std::move(temp_flattened);
                    current_indices = std::move(temp_indices);
                    current_total_length = temp_total_length;
                    current_count += static_cast<int>(input_data[i].size());
                    continue;
                } else {
                    flattener = IncrementalFlatten();
                    for (size_t list_idx = 0; list_idx < current_group.size();
                         ++list_idx) {
                        flattener.insert_list(current_group[list_idx],
                                              list_idx);
                    }
                    flattener.update_flattened();
                    current_flattened = flattener.get_flattened();
                    current_indices = flattener.get_indices();
                }
            }
            result.emplace_back(std::move(current_group));
            total_lengths.push_back(current_total_length);
            total_weights.push_back(flattener.get_total_weight());
            flattened_lists.emplace_back(std::move(current_flattened));
            index_lists.emplace_back(std::move(current_indices));

            current_group = input_data[i];
            current_count = static_cast<int>(input_data[i].size());

            flattener = IncrementalFlatten();
            for (size_t list_idx = 0; list_idx < current_group.size();
                 ++list_idx) {
                flattener.insert_list(current_group[list_idx], list_idx);
            }
            flattener.update_flattened();
            current_flattened = flattener.get_flattened();
            current_indices = flattener.get_indices();
            current_total_length = static_cast<int>(current_flattened.size());
        }

        if (!current_group.empty()) {
            result.emplace_back(std::move(current_group));
            total_lengths.push_back(current_total_length);
            total_weights.push_back(flattener.get_total_weight());
            flattened_lists.emplace_back(std::move(current_flattened));
            index_lists.emplace_back(std::move(current_indices));
        }
    } else {
        for (const auto &group : input_data) {
            if (group.empty()) {
                continue;
            }

            if (group.size() == 1) {
                const std::vector<int> &single_list = group[0];
                result.emplace_back(std::vector<std::vector<int>>{single_list});
                total_lengths.push_back(static_cast<int>(single_list.size()));
                flattened_lists.emplace_back(single_list);
                index_lists.emplace_back(std::vector<uint64_t>{1ULL});
                total_weights.push_back(single_list.size() *
                                        single_list.size());
            } else {
                IncrementalFlatten flattener;
                for (size_t list_idx = 0; list_idx < group.size(); ++list_idx) {
                    flattener.insert_list(group[list_idx], list_idx);
                }
                flattener.update_flattened();
                std::vector<int> merged_flattened = flattener.get_flattened();
                std::vector<uint64_t> merged_indices = flattener.get_indices();
                int merged_total_length =
                    static_cast<int>(merged_flattened.size());

                result.emplace_back(group);
                total_lengths.push_back(merged_total_length);
                total_weights.push_back(flattener.get_total_weight());
                flattened_lists.emplace_back(std::move(merged_flattened));
                index_lists.emplace_back(std::move(merged_indices));
            }
        }
    }

    return std::make_tuple(std::move(result), std::move(total_lengths),
                           std::move(total_weights), std::move(flattened_lists),
                           std::move(index_lists));
}

PYBIND11_MODULE(radix_merge, m) {
    m.doc() = "Radix merge implementation for integer lists with shared prefix "
              "optimization and bitmask indices";
    m.def(
        "radix_merge", &radix_merge,
        "Merge lists based on prefix matching and length/count constraints, "
        "considering shared prefixes and returning bitmask indices and weights",
        py::arg("input_data"), py::arg("min_prefix_match") = 0,
        py::arg("max_length") = 16384, py::arg("max_count") = 32,
        py::arg("allow_cross_group_merge") = true);
}
