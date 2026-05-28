use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Concept {
    name: String,
    desirability: f64,
    feasibility: f64,
    viability: f64,
    responsibility: f64,
    friction: f64,
    residual_risk: f64,
}

#[derive(Debug)]
struct ScoredConcept {
    name: String,
    value: f64,
    risk: f64,
}

fn combined_risk(c: &Concept) -> f64 {
    0.50 * c.friction + 0.50 * c.residual_risk
}

fn validation_value(c: &Concept) -> f64 {
    0.25 * c.desirability
        + 0.20 * c.feasibility
        + 0.20 * c.viability
        + 0.20 * c.responsibility
        - 0.15 * combined_risk(c)
}

fn parse_concepts(path: &str) -> Result<Vec<Concept>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut concepts = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 9 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        concepts.push(Concept {
            name: fields[0].trim().to_string(),
            desirability: fields[3].trim().parse()?,
            feasibility: fields[4].trim().parse()?,
            viability: fields[5].trim().parse()?,
            responsibility: fields[6].trim().parse()?,
            friction: fields[7].trim().parse()?,
            residual_risk: fields[8].trim().parse()?,
        });
    }

    Ok(concepts)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/validation_concepts_raw.csv".to_string());

    let concepts = parse_concepts(&path)?;
    let mut scored: Vec<ScoredConcept> = concepts
        .iter()
        .map(|c| ScoredConcept {
            name: c.name.clone(),
            value: validation_value(c),
            risk: combined_risk(c),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,concept,validation_value,combined_risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
