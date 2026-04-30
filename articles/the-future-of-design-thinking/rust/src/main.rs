fn design_value(human_relevance: f64, feasibility: f64, learning_value: f64, residual_risk: f64) -> f64 {
    0.35 * human_relevance + 0.25 * feasibility + 0.25 * learning_value - 0.15 * residual_risk
}

fn main() {
    let score = design_value(8.8, 7.4, 8.1, 4.0);
    println!("Design value: {:.3}", score);
}
