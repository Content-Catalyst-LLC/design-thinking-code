use std::env;
use std::error::Error;
use std::fs;

#[derive(Debug, Clone)]
struct Insight {
    name: String,
    pattern_support: f64,
    explanatory_depth: f64,
    opportunity_value: f64,
    interpretive_risk: f64,
}

#[derive(Debug)]
struct ScoredInsight {
    name: String,
    value: f64,
}

fn insight_value(insight: &Insight) -> f64 {
    0.30 * insight.pattern_support
        + 0.30 * insight.explanatory_depth
        + 0.25 * insight.opportunity_value
        - 0.15 * insight.interpretive_risk
}

fn parse_insights(path: &str) -> Result<Vec<Insight>, Box<dyn Error>> {
    let content = fs::read_to_string(path)?;
    let mut insights = Vec::new();

    for (idx, line) in content.lines().enumerate() {
        if idx == 0 || line.trim().is_empty() {
            continue;
        }

        let fields: Vec<&str> = line.split(',').collect();
        if fields.len() < 5 {
            return Err(format!("Malformed CSV row: {}", line).into());
        }

        insights.push(Insight {
            name: fields[0].trim().to_string(),
            pattern_support: fields[1].trim().parse()?,
            explanatory_depth: fields[2].trim().parse()?,
            opportunity_value: fields[3].trim().parse()?,
            interpretive_risk: fields[4].trim().parse()?,
        });
    }

    Ok(insights)
}

fn main() -> Result<(), Box<dyn Error>> {
    let path = env::args()
        .nth(1)
        .unwrap_or_else(|| "../data/raw/candidate_insights_raw.csv".to_string());

    let insights = parse_insights(&path)?;
    let mut scored: Vec<ScoredInsight> = insights
        .iter()
        .map(|i| ScoredInsight {
            name: i.name.clone(),
            value: insight_value(i),
        })
        .collect();

    scored.sort_by(|a, b| b.value.partial_cmp(&a.value).unwrap());

    println!("rank,insight,insight_value");
    for (idx, row) in scored.iter().enumerate() {
        println!("{},{},{:.6}", idx + 1, row.name, row.value);
    }

    Ok(())
}
