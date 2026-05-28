#include <algorithm>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

struct Row {
    std::string name;
    std::vector<double> v;
};

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::stringstream ss(line);
    std::string item;
    while (std::getline(ss, item, ',')) {
        fields.push_back(item);
    }
    return fields;
}

std::vector<Row> read_rows(const std::string& path) {
    std::ifstream file(path);
    if (!file) {
        throw std::runtime_error("Unable to open input file: " + path);
    }

    std::string line;
    std::getline(file, line);
    std::vector<Row> rows;

    while (std::getline(file, line)) {
        if (line.empty()) {
            continue;
        }
        auto fields = split_csv_line(line);
        if (fields.size() < 16) {
            throw std::runtime_error("Malformed CSV row: " + line);
        }

        Row row;
        row.name = fields[0];
        for (std::size_t i = 2; i < 16; ++i) {
            row.v.push_back(std::stod(fields[i]));
        }
        rows.push_back(row);
    }

    return rows;
}

int main(int argc, char** argv) {
    const std::string path = argc > 1 ? argv[1] : "../data/raw/future_design_initiatives_raw.csv";

    try {
        auto rows = read_rows(path);

        struct Scored {
            std::string name;
            double readiness;
            double stewardship_need;
            double ai_maturity;
            double priority;
        };

        std::vector<Scored> scored;

        for (const auto& row : rows) {
            const auto& v = row.v;
            double human = v[0], systems = v[1], evidence = v[2], ethics = v[3], ai = v[4];
            double implementation = v[5], public_value = v[6], stewardship = v[7], risk = v[8];
            double participation = v[9], learning = v[10], data = v[11], climate = v[12], burden = v[13];

            double readiness =
                0.11 * human + 0.12 * systems + 0.12 * evidence +
                0.12 * ethics + 0.10 * ai + 0.10 * implementation +
                0.12 * public_value + 0.09 * stewardship +
                0.06 * participation + 0.06 * learning +
                0.04 * data + 0.04 * climate + 0.04 * burden -
                0.10 * risk;

            double stewardship_need =
                0.26 * risk + 0.17 * (10 - stewardship) +
                0.15 * (10 - implementation) +
                0.12 * (10 - ethics) +
                0.10 * (10 - evidence) +
                0.08 * (10 - systems) +
                0.07 * (10 - learning) +
                0.05 * (10 - burden);

            double ai_maturity =
                0.28 * ai + 0.18 * evidence + 0.16 * data +
                0.14 * ethics + 0.12 * human + 0.12 * learning -
                0.10 * risk;

            double priority =
                0.36 * readiness + 0.20 * public_value +
                0.14 * ethics + 0.10 * systems + 0.08 * evidence +
                0.06 * participation - 0.10 * stewardship_need -
                0.06 * risk;

            scored.push_back({row.name, readiness, stewardship_need, ai_maturity, priority});
        }

        std::sort(scored.begin(), scored.end(), [](const Scored& a, const Scored& b) {
            return a.priority > b.priority;
        });

        std::cout << "rank,initiative,future_design_readiness,stewardship_need,ai_design_maturity,portfolio_priority\n";
        for (std::size_t i = 0; i < scored.size(); ++i) {
            std::cout << i + 1 << "," << scored[i].name << ","
                      << std::fixed << std::setprecision(6)
                      << scored[i].readiness << ","
                      << scored[i].stewardship_need << ","
                      << scored[i].ai_maturity << ","
                      << scored[i].priority << "\n";
        }
    } catch (const std::exception& ex) {
        std::cerr << "ERROR: " << ex.what() << "\n";
        return 1;
    }

    return 0;
}
