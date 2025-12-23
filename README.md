# Web Scraping of ISU Figure Skating Competition Results

## Quick Start
This project scrapes International Skating Union (ISU) figure skating competition results from the 2004–2005 season to the 2024–2025 season. For each competition, the data includes overall rankings and scores, as well as detailed protocols and judge information. These datasets are used for downstream analysis, such as investigating block judging and nationalistic bias.
```
# 1. Create environment and install dependencies
python -m venv .env
source .env/bin/activate # (macOS/Linux)
pip install -r requirements.txt

# 2. Run the pipeline
bash run_pipeline.sh
```

## Background
Figure skating is a sport in which skaters execute pre-planned technical elements (e.g., jumps, spins) within a choreographed routine set to music. There are typically two segments in each competition: short program/rhythm dance (SP) and long program/free dance (LP). Most competitions contain four disciplines: women, men, ice dance, and pairs. Under the International Skating Union Judging System (IJS), a panel of (typically) 9 judges gives two scores in each segment: the technical element score (TES) and the program component score (PCS). The TES reflects the difficulty and quality of execution for technical elements (such as jumps and spins, and the PCS evaluates the artistic and presentation aspects of the program.

In each season, the ISU holds approximately 18 Level-A competitions, the highest level of international competitions in the sport. These typically include 7 Junior Grand Prix (JGP) Series events, 6 Grand Prix (GP) Series events, the Grand Prix Final (GPF), the Four Continents Championships, the European Championships, the World Championships, and the Junior World Championships.

### Data
ISU publicizes the detailed competition results after each event, including not only the rankings and scores for each segment, but also the detailed protocols that document the scores given by each judge for each element.

<p align="center">
  <img src="figures/element_distribution_example.png" alt="Alt text" width="600"/>
  <br>
  <em>Figure 3: Element Distribution Example</em>
</p>
