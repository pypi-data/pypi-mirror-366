#include <omp.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <vector>

namespace py = pybind11;

double calculate_load(const std::vector<int> &cumsum_lengths,
                      const std::vector<int> &lengths, int sum_lengths,
                      int node_idx, int nodes) {
    double target_start = node_idx * (sum_lengths / (2.0 * nodes));
    double target_end = (node_idx + 1) * (sum_lengths / (2.0 * nodes));

    auto start_it = std::lower_bound(cumsum_lengths.begin(),
                                     cumsum_lengths.end(), target_start);
    int start_idx = std::max(
        0,
        static_cast<int>(std::distance(cumsum_lengths.begin(), start_it) - 1));

    auto end_it = std::lower_bound(cumsum_lengths.begin(), cumsum_lengths.end(),
                                   target_end);
    int end_idx = std::max(
        0, static_cast<int>(std::distance(cumsum_lengths.begin(), end_it) - 1));

    double calculate = 0;
    for (int i = start_idx; i < end_idx; ++i) {
        calculate += lengths[i] * lengths[i];
    }

    double delta_start = target_start - cumsum_lengths[start_idx];
    double delta_end = target_end - cumsum_lengths[end_idx];

    calculate -= delta_start * delta_start;
    calculate += delta_end * delta_end;

    return calculate;
}

double get_balance(const std::vector<int> &lengths, int nodes) {
    int sum_lengths = std::accumulate(lengths.begin(), lengths.end(), 0);

    std::vector<int> cumsum_lengths(lengths.size() + 1, 0);
    std::partial_sum(lengths.begin(), lengths.end(),
                     cumsum_lengths.begin() + 1);

    std::vector<double> calculations;
    calculations.reserve(nodes);

    for (int node_idx = 0; node_idx < nodes; ++node_idx) {
        double load = calculate_load(cumsum_lengths, lengths, sum_lengths,
                                     node_idx, nodes) +
                      calculate_load(cumsum_lengths, lengths, sum_lengths,
                                     2 * nodes - node_idx - 1, nodes);
        calculations.push_back(load);
    }

    double avg_load =
        std::accumulate(calculations.begin(), calculations.end(), 0.0) /
        calculations.size();
    double max_diff = 0;
    for (double calculate : calculations) {
        max_diff = std::max(max_diff, std::abs(calculate - avg_load));
    }

    return max_diff;
}

std::vector<int> balance_single_list(const std::vector<int> &input_lengths,
                                     int nodes) {
    std::vector<int> best_lengths = input_lengths;
    double best_balance = std::numeric_limits<double>::infinity();

    std::vector<int> current = input_lengths;

    for (size_t i = 0; i < current.size(); ++i) {
        std::swap(current[i], current.back());
        double balance = get_balance(current, nodes);
        if (balance < best_balance) {
            best_balance = balance;
            best_lengths = current;
        }
        std::swap(current[i], current.back());
    }

    return best_lengths;
}

std::vector<std::vector<int>>
load_balance_parallel(const std::vector<std::vector<int>> &input_data,
                      int nodes, bool enable_parallel) {
    std::vector<std::vector<int>> result(input_data.size());

    if (enable_parallel) {
#pragma omp parallel for
        for (size_t i = 0; i < input_data.size(); ++i) {
            const auto &lengths = input_data[i];
            if (!lengths.empty()) {
                result[i] = balance_single_list(lengths, nodes);
            }
        }
    } else {
        for (size_t i = 0; i < input_data.size(); ++i) {
            const auto &lengths = input_data[i];
            if (!lengths.empty()) {
                result[i] = balance_single_list(lengths, nodes);
            }
        }
    }

    result.erase(
        std::remove_if(result.begin(), result.end(),
                       [](const std::vector<int> &v) { return v.empty(); }),
        result.end());

    return result;
}

std::vector<std::vector<int>>
load_balance(const std::vector<std::vector<int>> &input_data, int nodes,
             bool enable_parallel = true) {
    if (input_data.empty()) {
        return {};
    }

    return load_balance_parallel(input_data, nodes, enable_parallel);
}

std::vector<int> load_balance(const std::vector<int> &input_data, int nodes) {
    if (input_data.empty()) {
        return {};
    }
    return balance_single_list(input_data, nodes);
}

std::vector<std::vector<std::vector<int>>>
load_balance(const std::vector<std::vector<std::vector<int>>> &input_data,
             int nodes, bool enable_parallel = true) {
    if (input_data.empty()) {
        return {};
    }

    std::vector<std::vector<std::vector<int>>> result(input_data.size());

    if (enable_parallel) {
#pragma omp parallel for
        for (size_t i = 0; i < input_data.size(); ++i) {
            const auto &data_2d = input_data[i];
            if (!data_2d.empty()) {
                result[i] = load_balance_parallel(data_2d, nodes, false);
            }
        }
    } else {
        for (size_t i = 0; i < input_data.size(); ++i) {
            const auto &data_2d = input_data[i];
            if (!data_2d.empty()) {
                result[i] = load_balance_parallel(data_2d, nodes, false);
            }
        }
    }

    result.erase(std::remove_if(result.begin(), result.end(),
                                [](const std::vector<std::vector<int>> &v) {
                                    return v.empty();
                                }),
                 result.end());

    return result;
}

PYBIND11_MODULE(load_balance, m) {
    m.doc() = "Load balancing algorithm implementation";
    m.def("load_balance",
          py::overload_cast<const std::vector<std::vector<std::vector<int>>> &,
                            int, bool>(&load_balance),
          "Load balancing algorithm for 3D integer lists",
          py::arg("input_data"), py::arg("nodes") = 2,
          py::arg("enable_parallel") = true);
    m.def("load_balance",
          py::overload_cast<const std::vector<std::vector<int>> &, int, bool>(
              &load_balance),
          "Load balancing algorithm for 2D integer lists",
          py::arg("input_data"), py::arg("nodes") = 2,
          py::arg("enable_parallel") = true);
    m.def("load_balance",
          py::overload_cast<const std::vector<int> &, int>(&load_balance),
          "Load balancing algorithm for 1D integer list", py::arg("input_data"),
          py::arg("nodes") = 2);
}
