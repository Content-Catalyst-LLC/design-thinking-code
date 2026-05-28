use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Idea {
    name: String,
    desirability: f64,
    feasibility: f64,
    novelty: f64,
    equity_value: f64,
    learning_value: f64,
    residual_risk: f64,
}

#[derive(Debug)]
struct ScoredIdea {
    name: String,
    value: f64,
}

fn idea_value(idea: &Idea) -> f64 {
    0.24 * idea.desirability
        + 0.18 * idea.feasibility
        + 0.18 * idea.novelty
        + 0.18 * idea.equity_value
        + 0.12 * idea.learning_value
        - 0.10 * idea.residual_risk
}

fn parse_ideas(path: &str) -> Result<Vec<Idea>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut ideas = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 8 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        ideas.push(Idea {
            name: fields[0].trim().to_string(),
            desirability: fields[2].trim().parse()?,
            feasibility: fields[3].trim().parse()?,
            novelty: fields[4].trim().parse()?,
            equity_value: fields[5].trim().parse()?,
            learning_value: fields[6].trim().parse()?,
            residual_risk: fields[7].trim().parse()?,
        });
    }

    Ok(ideas)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/idea_portfolio_raw.csv".to_string());

    let ideas = parse_ideas(&path)?;
    let mut scored: Vec<ScoredIdea> = ideas
        .iter()
        .map(|i| ScoredIdea {
            name: i.name.clone(),
            value: idea_value(i),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,idea,idea_value");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6}", idx + 1, row.name, row.value);
    }

    Ok(())
}
