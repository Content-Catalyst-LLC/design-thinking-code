use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct InnovationConcept {
    name: String,
    desirability: f64,
    feasibility: f64,
    viability: f64,
    equity: f64,
    learning_value: f64,
    implementation_readiness: f64,
    risk: f64,
}

#[derive(Debug)]
struct ScoredConcept {
    name: String,
    value: f64,
    risk: f64,
}

fn design_value(x: &InnovationConcept) -> f64 {
    0.22 * x.desirability
        + 0.16 * x.feasibility
        + 0.16 * x.viability
        + 0.18 * x.equity
        + 0.12 * x.learning_value
        + 0.10 * x.implementation_readiness
        - 0.06 * x.risk
}

fn parse_concepts(path: &str) -> Result<Vec<InnovationConcept>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut concepts = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 10 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        concepts.push(InnovationConcept {
            name: fields[0].trim().to_string(),
            desirability: fields[3].trim().parse()?,
            feasibility: fields[4].trim().parse()?,
            viability: fields[5].trim().parse()?,
            equity: fields[6].trim().parse()?,
            learning_value: fields[7].trim().parse()?,
            implementation_readiness: fields[8].trim().parse()?,
            risk: fields[9].trim().parse()?,
        });
    }

    Ok(concepts)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/organizational_innovation_concepts_raw.csv".to_string());

    let concepts = parse_concepts(&path)?;
    let mut scored: Vec<ScoredConcept> = concepts
        .iter()
        .map(|x| ScoredConcept {
            name: x.name.clone(),
            value: design_value(x),
            risk: x.risk,
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,concept,design_value,risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
