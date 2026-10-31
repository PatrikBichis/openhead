# Status

**Title:** Status

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Device status, up to 1 Hz. Also the result of `system.status`. Every payload field is present unless the subscription named `fields`; then only those are.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Status > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Status > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Status > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Status > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Status > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type             | Deprecated | Definition                             | Title/Description                                                                     |
| ------------------------------------------- | ------- | ---------------- | ---------- | -------------------------------------- | ------------------------------------------------------------------------------------- |
| - [battery_level](#allOf_i1_battery_level ) | No      | number           | No         | -                                      | Omitted when unknown (e.g. simulator).                                                |
| - [charging](#allOf_i1_charging )           | No      | boolean          | No         | -                                      | -                                                                                     |
| - [thermal_state](#allOf_i1_thermal_state ) | No      | enum (of string) | No         | In ../common.json#/$defs/thermal_state | -                                                                                     |
| - [view](#allOf_i1_view )                   | No      | enum (of string) | No         | In ../common.json#/$defs/view          | What fills the screen.                                                                |
| - [overlay](#allOf_i1_overlay )             | No      | enum (of string) | No         | -                                      | -                                                                                     |
| - [subtitle](#allOf_i1_subtitle )           | No      | string           | No         | -                                      | Subtitle text on screen. Omitted when none.                                           |
| - [theme](#allOf_i1_theme )                 | No      | string           | No         | In ../common.json#/$defs/name          | Lower-case identifier used for themes and emotions.                                   |
| - [emotion](#allOf_i1_emotion )             | No      | string           | No         | Same as [theme](#allOf_i1_theme )      | Lower-case identifier used for themes and emotions.                                   |
| - [mode](#allOf_i1_mode )                   | No      | enum (of string) | No         | In ../common.json#/$defs/mode          | Camera ownership mode. Only \`idle\` is supported in 0.1.                             |
| - [dev_mode](#allOf_i1_dev_mode )           | No      | boolean          | No         | -                                      | -                                                                                     |
| - [clients](#allOf_i1_clients )             | No      | integer          | No         | -                                      | Connected, authenticated clients.                                                     |
| - [rtt_ms](#allOf_i1_rtt_ms )               | No      | number           | No         | -                                      | Round-trip time to the receiving client, from WebSocket ping. Omitted until measured. |
| - [uptime_s](#allOf_i1_uptime_s )           | No      | number           | No         | -                                      | -                                                                                     |

### <a name="allOf_i1_battery_level"></a>2.1. Property `Status > allOf > item 1 > battery_level`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Omitted when unknown (e.g. simulator).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

### <a name="allOf_i1_charging"></a>2.2. Property `Status > allOf > item 1 > charging`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

### <a name="allOf_i1_thermal_state"></a>2.3. Property `Status > allOf > item 1 > thermal_state`

|                |                                     |
| -------------- | ----------------------------------- |
| **Type**       | `enum (of string)`                  |
| **Required**   | No                                  |
| **Defined in** | ../common.json#/$defs/thermal_state |

Must be one of:
* "nominal"
* "fair"
* "serious"
* "critical"

### <a name="allOf_i1_view"></a>2.4. Property `Status > allOf > item 1 > view`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `enum (of string)`         |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/view |

**Description:** What fills the screen.

Must be one of:
* "face"
* "image"
* "video"
* "web"

### <a name="allOf_i1_overlay"></a>2.5. Property `Status > allOf > item 1 > overlay`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "none"
* "face-corner"

### <a name="allOf_i1_subtitle"></a>2.6. Property `Status > allOf > item 1 > subtitle`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Subtitle text on screen. Omitted when none.

| Restrictions   |      |
| -------------- | ---- |
| **Max length** | 4000 |

### <a name="allOf_i1_theme"></a>2.7. Property `Status > allOf > item 1 > theme`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/name |

**Description:** Lower-case identifier used for themes and emotions.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

### <a name="allOf_i1_emotion"></a>2.8. Property `Status > allOf > item 1 > emotion`

|                        |                          |
| ---------------------- | ------------------------ |
| **Type**               | `string`                 |
| **Required**           | No                       |
| **Same definition as** | [theme](#allOf_i1_theme) |

**Description:** Lower-case identifier used for themes and emotions.

### <a name="allOf_i1_mode"></a>2.9. Property `Status > allOf > item 1 > mode`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `enum (of string)`         |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/mode |

**Description:** Camera ownership mode. Only `idle` is supported in 0.1.

Must be one of:
* "idle"
* "sensing"
* "capture"

### <a name="allOf_i1_dev_mode"></a>2.10. Property `Status > allOf > item 1 > dev_mode`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

### <a name="allOf_i1_clients"></a>2.11. Property `Status > allOf > item 1 > clients`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

**Description:** Connected, authenticated clients.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_rtt_ms"></a>2.12. Property `Status > allOf > item 1 > rtt_ms`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Round-trip time to the receiving client, from WebSocket ping. Omitted until measured.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_uptime_s"></a>2.13. Property `Status > allOf > item 1 > uptime_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Status > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"status"`

----------------------------------------------------------------------------------------------------------------------------
