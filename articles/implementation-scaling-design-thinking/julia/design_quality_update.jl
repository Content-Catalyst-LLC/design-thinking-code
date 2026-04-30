# Toy design-quality update model.
# Educational only.

solution_quality = 0.35
insight_gain = 0.70
usability_improvement = 0.65
new_friction = 0.25
learning_rate = 0.08

for t in 1:16
    solution_quality = solution_quality +
        learning_rate * (0.45 * insight_gain + 0.40 * usability_improvement - 0.35 * new_friction)
    solution_quality = clamp(solution_quality, 0.0, 1.0)
    println("Iteration ", t, ": solution quality = ", round(solution_quality, digits=3))
end
