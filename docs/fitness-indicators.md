# Fitness indicators

Locked by ADR 0008. Add, remove, or move a row here. Do not add a weight column. The score is the rung.

Each row is labeled `effectiveness` or `efficiency` by ADR 0010. A row counts only when the evidence is definitive. A new row waits until the practice maintainer and the judgment agent confirm it.

Plain-language meaning and remediation: `docs/fitness/<id>.md`.

A practice row is required for its rung. A failure row on rung N holds the session on N-1.

| Id | Rung | Result | Kind | Item | Check |
| --- | --- | --- | --- | --- | --- | --- |
| P01 | 1 | effectiveness | practice | The end state is named, including by questions that build it | A series of prompts names a finished condition, or asks for the list, the edge, or the missing piece of one. A question counts as practice. One prompt does not have to hold the whole scope |
| F01 | 1 | effectiveness | failure | No end state | The series never names a finished condition and the questions are not aimed at completing one |
| P02 | 2 | effectiveness | practice | The check can fail | The human text contains a condition that could be false |
| F02 | 2 | effectiveness | failure | A check that cannot fail | Done is "looks good" or the agent's own summary |
| P03 | 3 | effectiveness | practice | One outcome is in force | Several end states are ordered or split |
| F03 | 3 | effectiveness | failure | Two outcomes treated as one | Two end states are in force and never ordered or split |
| P04 | 3 | efficiency | practice | The deciding fact is present before the agent acts | The fact that changes the work appears before a rejected attempt |
| F04 | 3 | efficiency | failure | The deciding fact arrives late | That fact appears only after a rejected attempt |
| P05 | 3 | effectiveness | practice | The example agrees with the rule | A supplied example would pass the instruction it sits under |
| F05 | 3 | effectiveness | failure | The example fights the rule | The supplied example would fail that instruction |
| P06 | 3 | effectiveness | practice | The path leaves the goal intact | Steps, when present, leave the end state reachable |
| F06 | 3 | effectiveness | failure | The path replaces the goal | The steps are specified and the end state is missing or unreachable |
| F07 | 3 | effectiveness | failure | A contradiction left standing | Two instructions remain and cannot both be true |
| P07 | 4 | effectiveness | practice | The outcome lands | A later human turn accepts the result, or the stated check is met |
| F08 | 4 | efficiency | failure | Rejected, and the next prompt repeats the brief | A rejection is followed by the original ask unchanged |
| F09 | 4 | effectiveness | failure | The goal moves and the old one is not dropped | A new end state appears without dropping the old one |
| F10 | 4 | effectiveness | failure | Accepted, then replaced | An acceptance is followed by the result being thrown out |
| F11 | 4 | effectiveness | failure | Gate-green, and the human still rejects the result | A tool result passes, and a later human turn rejects the outcome |
| P08 | 5 | efficiency | practice | Unchanged policy is read, not pasted | A tool result contains the record, and the prompt points at it without its text |
| P09 | 5 | efficiency | practice | The first statement of a new fact | The fact appears once, and no earlier turn or tool result contained it |
| F12 | 5 | efficiency | failure | The store is pasted as well as named | The prompt names the record and includes its text |
| F13 | 5 | efficiency | failure | The human repeats an unchanged fact | The same fact appears again later and nothing about it changed |
| F14 | 5 | effectiveness | failure | A citation misses the record | The named decision is not in the tool result that read the record |
| F15 | 5 | efficiency | failure | Ceremony | Process narration adds no constraint and removes none |
| P10 | 6 | efficiency | practice | The opening turn is a pointer | The first human turn is a continuation, a skill name, or an id, and the next tool reads the packet or the store |
| P11 | 6 | efficiency | practice | The procedure is invoked, not pasted | The human names the skill or command, the procedure text is absent, and a tool runs that command |
| P12 | 6 | efficiency | practice | A bound fact is not re-answered | The agent asks for a fact already in a tool result, and the human points at the record |
| P13 | 7 | effectiveness | practice | The check is a command that a tool runs | The human names an existing command and a tool result is its output |
| P14 | 7 | effectiveness | practice | The accept comes after that result | The accepting turn follows the tool result, not the agent's summary alone |
| P15 | 7 | effectiveness | practice | The miss is named as the failing check | The correction cites the command and the failing line |
| P16 | 8 | efficiency | practice | A correction names only the miss | The repair turn does not include the original brief |
| F16 | 8 | efficiency | failure | A correction restates the original brief | The repair turn repeats the original ask |
| P17 | 8 | effectiveness | practice | The miss or new fact is written to the store | A tool writes a decision, rule, or fact |
| P18 | 8 | effectiveness | practice | The writer and the checker are different passes | The pass that writes and the pass that checks are different tool calls |
| F17 | 8 | effectiveness | failure | The prompt is the patch | The human pastes the corrected line, command, or config |
| F18 | 8 | effectiveness | failure | The human says they already fixed it | A later turn claims a human fix that no earlier turn stated as the outcome |
| F19 | 8 | efficiency | failure | The same miss is corrected a second time | Two human turns correct the same mistake, and the first was not written to the store |
| F20 | 8 | effectiveness | failure | The miss stays in the chat | A new decision or fact never appears in a write |
| F21 | 8 | efficiency | failure | A stored rule has to be stated again | The human states a rule already present in a tool result |
| P19 | 9 | effectiveness | practice | The new record is obeyed | A later tool reads the record written earlier, and no human turn between them restates it |
| P20 | 9 | efficiency | practice | The non-goal arrives before the extra build | The human says what not to build, and those paths are not written |
| P21 | 9 | effectiveness | practice | The boundary holds | Every later write stays inside the one path, id, or artifact the human named |
| P22 | 10 | efficiency | practice | The accept or reject is the whole prompt | After a drafted record or product, the human turn only accepts or rejects it |

Not indicators, and not rows: a short prompt, a long prompt, a polite prompt, an unread file, and a success with no stated outcome.

Not checked from the current extract, and not rows: a silent edit outside the agent, a silent revert, and a workaround the human never mentions.
