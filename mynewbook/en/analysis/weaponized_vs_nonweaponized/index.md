# Weaponized vs. Non-weaponized analysis

## Chapter map
- Datasets overview
- User contributions
- User metadata
- User motivations
- Co-edited graph analysis
- IP geolocation

## Objectives
- Identify robust signals for detection models
- Compare user types (registered / IP / bots)
- Validate representativeness (small vs large)

## Data & labels used
- Small database
- Large database
- Weaponized / Not weaponized labels
- Notes on label limitations

## Analyses included
### Datasets overview
- Temporal distributions
- Summary statistics tables

### Data exploration
- Distributions by user type
- Statistical tests (e.g., chi-square)
- Temporal/weekly heatmaps

### Users contributions
- Top contributors profiling
- Ukraine/Russia topical focus
- Edit sizes and temporal behavior
- ORES/quality auxiliary signals

### Users metadata
- Account age vs editcount patterns
- Blocks and group membership notes
- Gender / disclosure caveats

### Users motivations
- User pages / talk pages signals
- Qualitative + lightweight computational summaries
- Ethical boundaries (no intent inference)

### Co-edited graph analysis
- Graph construction choices
- Community detection (Leiden)
- Cluster interpretation

### IP address geolocation
- Method
- Biases and limitations

## Notebooks in this chapter
- {ref}`datasets_overview`
- {ref}`data_exploration`
- {ref}`users_contributions`
- {ref}`users_metadata`
- {ref}`users_motivations`
- {ref}`coedited_graph`
- {ref}`ip_geolocation`

## Outputs
- Figures (time series, distributions, heatmaps)
- Tables (summary stats, top users)
- Graph exports (Gephi-ready files)
