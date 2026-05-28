use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Pathway {
    name: String,
    human_relevance: f64,
    feasibility: f64,
    learning_value: f64,
    residual_risk: f64,
}

#[derive(Debug)]
struct ScoredPathway {
    name: String,
    value: f64,
}

fn design_value(pathway: &Pathway) -> f64 {
    0.35 * pathway.human_relevance
        + 0.25 * pathway.feasibility
        + 0.25 * pathway.learning_value
        - 0.15 * pathway.residual_risk
}

fn parse_pathways(path: &str) -> Result<Vec<Pathway>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut pathways = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 5 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        pathways.push(Pathway {
            name: fields[0].trim().to_string(),
            human_relevance: fields[1].trim().parse()?,
            feasibility: fields[2].trim().parse()?,
            learning_value: fields[3].trim().parse()?,
            residual_risk: fields[4].trim().parse()?,
        });
    }

    Ok(pathways)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/design_pathways_raw.csv".to_string());

    let pathways = parse_pathways(&path)?;
    let mut scored: Vec<ScoredPathway> = pathways
        .iter()
        .map(|p| ScoredPathway {
            name: p.name.clone(),
            value: design_value(p),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,pathway,design_value");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6}", idx + 1, row.name, row.value);
    }

    Ok(())
}
