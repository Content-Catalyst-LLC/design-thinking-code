use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Concept {
    name: String,
    usability: f64,
    feasibility: f64,
    ecological_benefit: f64,
    circularity: f64,
    equity: f64,
    durability: f64,
    risk: f64,
}

#[derive(Debug)]
struct ScoredConcept {
    name: String,
    value: f64,
    risk: f64,
}

fn sustainability_value(x: &Concept) -> f64 {
    0.16 * x.usability
        + 0.16 * x.feasibility
        + 0.24 * x.ecological_benefit
        + 0.16 * x.circularity
        + 0.14 * x.equity
        + 0.08 * x.durability
        - 0.06 * x.risk
}

fn parse_concepts(path: &str) -> Result<Vec<Concept>, Box<dyn Error>> {
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

        concepts.push(Concept {
            name: fields[0].trim().to_string(),
            usability: fields[3].trim().parse()?,
            feasibility: fields[4].trim().parse()?,
            ecological_benefit: fields[5].trim().parse()?,
            circularity: fields[6].trim().parse()?,
            equity: fields[7].trim().parse()?,
            durability: fields[8].trim().parse()?,
            risk: fields[9].trim().parse()?,
        });
    }

    Ok(concepts)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/sustainability_concepts_raw.csv".to_string());

    let concepts = parse_concepts(&path)?;
    let mut scored: Vec<ScoredConcept> = concepts
        .iter()
        .map(|x| ScoredConcept {
            name: x.name.clone(),
            value: sustainability_value(x),
            risk: x.risk,
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,concept,sustainability_value,risk");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6},{:.6}", idx + 1, row.name, row.value, row.risk);
    }

    Ok(())
}
