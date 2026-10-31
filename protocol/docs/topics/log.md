# Log

**Title:** Log

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** One structured log line, sent as it happens. Every received command is logged with its `seq` in `seq_ref`.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [payload](#allOf_i1)  |

## <a name="allOf_i0"></a>1. Property `Log > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Log > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Log > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Log > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Log > allOf > payload`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/payload  |

| Property                            | Pattern | Type             | Deprecated | Definition                         | Title/Description                                   |
| ----------------------------------- | ------- | ---------------- | ---------- | ---------------------------------- | --------------------------------------------------- |
| + [time_ms](#allOf_i1_time_ms )     | No      | integer          | No         | -                                  | When the line was logged.                           |
| + [level](#allOf_i1_level )         | No      | enum (of string) | No         | In ../common.json#/$defs/log_level | -                                                   |
| + [subsystem](#allOf_i1_subsystem ) | No      | string           | No         | -                                  | e.g. \`link\`, \`face\`, \`display\`, \`sensors\`.  |
| + [message](#allOf_i1_message )     | No      | string           | No         | -                                  | -                                                   |
| - [seq_ref](#allOf_i1_seq_ref )     | No      | integer          | No         | -                                  | \`seq\` of the received message this line is about. |

### <a name="allOf_i1_time_ms"></a>2.1. Property `Log > allOf > item 1 > time_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** When the line was logged.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_level"></a>2.2. Property `Log > allOf > item 1 > level`

|                |                                 |
| -------------- | ------------------------------- |
| **Type**       | `enum (of string)`              |
| **Required**   | Yes                             |
| **Defined in** | ../common.json#/$defs/log_level |

Must be one of:
* "debug"
* "info"
* "notice"
* "warning"
* "error"
* "fault"

### <a name="allOf_i1_subsystem"></a>2.3. Property `Log > allOf > item 1 > subsystem`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** e.g. `link`, `face`, `display`, `sensors`.

| Restrictions                      |                                                                                               |
| --------------------------------- | --------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_.]*$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_.%5D%2A%24) |

### <a name="allOf_i1_message"></a>2.4. Property `Log > allOf > item 1 > message`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions   |      |
| -------------- | ---- |
| **Max length** | 4096 |

### <a name="allOf_i1_seq_ref"></a>2.5. Property `Log > allOf > item 1 > seq_ref`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

**Description:** `seq` of the received message this line is about.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Log > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"log"`

----------------------------------------------------------------------------------------------------------------------------
