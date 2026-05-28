use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct DesignOption {
    name: String,
    human_benefit: f64,
    usability: f64,
    stakeholder_fit: f64,
    burden: f64,
}

#[derive(Debug)]
struct ScoredOption {
    name: String,
    value: f64,
}

fn human_centered_value(option: &DesignOption) -> f64 {
    0.30 * option.human_benefit
        + 0.25 * option.usability
        + 0.30 * option.stakeholder_fit
        - 0.15 * option.burden
}

fn parse_options(path: &str) -> Result<Vec<DesignOption>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut options = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 5 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        options.push(DesignOption {
            name: fields[0].trim().to_string(),
            human_benefit: fields[1].trim().parse()?,
            usability: fields[2].trim().parse()?,
            stakeholder_fit: fields[3].trim().parse()?,
            burden: fields[4].trim().parse()?,
        });
    }

    Ok(options)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/human_centered_options_raw.csv".to_string());

    let options = parse_options(&path)?;
    let mut scored: Vec<ScoredOption> = options
        .iter()
        .map(|o| ScoredOption {
            name: o.name.clone(),
            value: human_centered_value(o),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,option,hc_value");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6}", idx + 1, row.name, row.value);
    }

    Ok(())
}
