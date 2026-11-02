# Speech

**Title:** Speech

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Speaking and listening, as events (no rate). Speaking: `say_start` when an utterance begins, `cue` when a segment that is not text is reached (`cue_type` emotion, action or gesture, and `cue` its name), `say_end` when it is done (`interrupted` if stopped or replaced). Listening: `partial` with the words so far while someone talks, `heard` with the final text when they pause.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Speech > allOf > Envelope`

**Title:** Envelope

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | ../envelope.json |

**Description:** Fields carried by every OpenHead message.

| Property                  | Pattern | Type    | Deprecated | Definition | Title/Description                                            |
| ------------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#allOf_i0_type ) | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#allOf_i0_ts )     | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#allOf_i0_seq )   | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.        |

### <a name="allOf_i0_type"></a>1.1. Property `Speech > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Speech > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Speech > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Speech > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type             | Deprecated | Definition | Title/Description                                     |
| ------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ----------------------------------------------------- |
| - [event](#allOf_i1_event )                 | No      | enum (of string) | No         | -          | -                                                     |
| - [utterance_id](#allOf_i1_utterance_id )   | No      | string           | No         | -          | Speaking events: the id \`speech.say\` answered with. |
| - [cue_type](#allOf_i1_cue_type )           | No      | enum (of string) | No         | -          | -                                                     |
| - [cue](#allOf_i1_cue )                     | No      | string           | No         | -          | With \`cue\`: the emotion, action or gesture name.    |
| - [interrupted](#allOf_i1_interrupted )     | No      | boolean          | No         | -          | With \`say_end\`.                                     |
| - [text](#allOf_i1_text )                   | No      | string           | No         | -          | With \`partial\` and \`heard\`: what was heard.       |
| - [confidence](#allOf_i1_confidence )       | No      | number           | No         | -          | With \`heard\`, when the recogniser gives one.        |
| - [sensor_time_s](#allOf_i1_sensor_time_s ) | No      | number           | No         | -          | Device clock, seconds.                                |

### <a name="allOf_i1_event"></a>2.1. Property `Speech > allOf > item 1 > event`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "say_start"
* "cue"
* "say_end"
* "partial"
* "heard"

### <a name="allOf_i1_utterance_id"></a>2.2. Property `Speech > allOf > item 1 > utterance_id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Speaking events: the id `speech.say` answered with.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

### <a name="allOf_i1_cue_type"></a>2.3. Property `Speech > allOf > item 1 > cue_type`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "emotion"
* "action"
* "gesture"

### <a name="allOf_i1_cue"></a>2.4. Property `Speech > allOf > item 1 > cue`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** With `cue`: the emotion, action or gesture name.

| Restrictions   |    |
| -------------- | -- |
| **Max length** | 64 |

### <a name="allOf_i1_interrupted"></a>2.5. Property `Speech > allOf > item 1 > interrupted`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

**Description:** With `say_end`.

### <a name="allOf_i1_text"></a>2.6. Property `Speech > allOf > item 1 > text`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** With `partial` and `heard`: what was heard.

| Restrictions   |      |
| -------------- | ---- |
| **Max length** | 4000 |

### <a name="allOf_i1_confidence"></a>2.7. Property `Speech > allOf > item 1 > confidence`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** With `heard`, when the recogniser gives one.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

### <a name="allOf_i1_sensor_time_s"></a>2.8. Property `Speech > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Device clock, seconds.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Speech > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"speech"`

----------------------------------------------------------------------------------------------------------------------------
