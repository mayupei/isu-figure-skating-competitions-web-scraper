# Web Scraping of ISU Figure Skating Competition Results

## Quick Start
This project scrapes International Skating Union (ISU) figure skating competition results from the 2004–2005 season to the 2024–2025 season. For each competition, the data includes overall rankings and scores, as well as detailed protocols (scoring sheets that document the score given by each judge for each element) and judges' information. These datasets are used for downstream analysis, such as investigating block judging and nationalistic bias.
```
# 1. Create environment and install dependencies
python -m venv .env
source .env/bin/activate # (macOS/Linux)
pip install -r requirements.txt

# 2. Run the pipeline
cd scripts
bash run_pipeline.sh
```

## Background
Figure skating is a sport in which skaters execute pre-planned technical elements (e.g., jumps, spins) within a choreographed routine set to music. There are typically two segments in each competition: short program/rhythm dance (SP) and long program/free dance (LP).[^1] Most competitions contain four disciplines: women, men, ice dance, and pairs. Under the ISU Judging System (IJS), a panel of (typically) 9 judges gives two scores in each segment: the technical element score (TES) and the program component score (PCS). The TES reflects the difficulty and quality of execution for technical elements (such as jumps and spins), and the PCS evaluates the artistic and presentation aspects of the program.

In each season, the ISU holds approximately 18 Level-A competitions, the highest level of international competitions in the sport. These typically include 7 Junior Grand Prix (JGP) Series events, 6 Grand Prix (GP) Series events, the Grand Prix Final (GPF), the Four Continents Championships, the European Championships, the World Championships, and the Junior World Championships.

## Web Scraping
### Data
ISU publicizes the detailed competition results after each event, including not only final rankings and scores, but also the detailed protocols that document the scores given by each judge for each element. Figure 1 shows the information publicized by ISU for Grand Prix (GP) Canada (click [here](https://www.isuresults.com/results/season2425/gpcan2024/) to see the original webpage). We can see that for each discipline, ISU documents (a) the entries (atheletes participated in the competition); (b) the overal ranking and scores; (c) judges' information; (d) the ranking and scores by segments; and (e) protocols.

Among these five components, judges’ information and protocols are the most informative. They not only contain detailed, element-by-element scores assigned by each judge, but also allow us to derive higher-level information found in the other components, such as skaters’ nationalities, segment rankings, and segment scores. Because judges’ information and protocols already subsume the content of the remaining components, I focus on these two sources for data collection.

For each competition, I download all information available as either HTML and PDF files and apply web scraping and and PDF scraping to reconstruct the judges' information and protocols into tabular forms.

<p align="center">
  <img src="screenshots/gpcan.jpg" alt="Alt text" width="800"/>
  <br>
  <em>Figure 1: Competition Results Available for GP Canada 2025</em>
</p>

[^1]: Before the 2011-2013 season, the ice dance had three segments: compulsory dance (CD), original dance (OD) and free dance (FD).