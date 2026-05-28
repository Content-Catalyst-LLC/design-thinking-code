# Data Dictionary

## `service_journey_stages_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `stage` | string | Service journey stage. |
| `stage_order` | integer | Stage order in the service journey. |
| `channel` | string | Primary channel for the stage. |
| `completion_probability` | numeric | Probability that users successfully complete the stage. |
| `clarity` | numeric | 1-10 score for legibility, instructions, and status clarity. |
| `trust` | numeric | 1-10 score for perceived trust and credibility. |
| `accessibility` | numeric | 1-10 score for access across abilities, language, devices, and support needs. |
| `user_burden` | numeric | 1-10 score for user effort and administrative burden. |
| `staff_load` | numeric | 1-10 score for staff workload and delivery burden. |
| `recovery_quality` | numeric | 1-10 score for recovery when the service fails. |
| `frontstage_quality` | numeric | 1-10 score for visible user-facing quality. |
| `backstage_readiness` | numeric | 1-10 score for internal readiness to deliver the stage. |
| `policy_complexity` | numeric | 1-10 score for policy or rule complexity. |
| `data_dependency` | numeric | 1-10 score for data or system dependency. |

## `service_user_groups_raw.csv`

| Column | Type | Description |
|---|---:|---|
| `group` | string | User, stakeholder, staff, or affected group. |
| `affectedness` | numeric | 0-1 degree to which the group is affected by service quality. |
| `completion_rate` | numeric | 0-1 service completion rate for the group. |
| `clarity` | numeric | 1-10 clarity score. |
| `accessibility` | numeric | 1-10 accessibility score. |
| `trust` | numeric | 1-10 trust score. |
| `burden` | numeric | 1-10 user or stakeholder burden score. |
| `recovery_access` | numeric | 1-10 access to recovery or correction. |
| `assisted_support` | numeric | 1-10 availability of human or assisted support. |
| `device_access` | numeric | 1-10 device and connectivity access. |
| `language_access` | numeric | 1-10 language access. |
| `disability_access` | numeric | 1-10 disability access. |
