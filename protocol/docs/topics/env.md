# Env

**Title:** Env

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Barometer, magnetometer and compass, up to 10 Hz. A field is left out when the device lacks the sensor or has no reading yet; the barometer needs Motion & Fitness access, which the first subscription asks for. Magnetic field in the `imu` device frame (+x right, +y up, +z out of the screen, portrait). Every available field is present unless the subscription named `fields`.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Env > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Env > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Env > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Env > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Env > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                                  | Pattern | Type             | Deprecated | Definition | Title/Description                                                                                             |
| --------------------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ------------------------------------------------------------------------------------------------------------- |
| - [pressure_kpa](#allOf_i1_pressure_kpa )                 | No      | number           | No         | -          | Air pressure in kilopascals.                                                                                  |
| - [relative_altitude_m](#allOf_i1_relative_altitude_m )   | No      | number           | No         | -          | Change in altitude in metres since the barometer started (this subscription or an earlier one still running). |
| - [magnetic_field_ut](#allOf_i1_magnetic_field_ut )       | No      | array of number  | No         | -          | Raw magnetic field in microtesla, device frame; includes the device's own bias.                               |
| - [heading_deg](#allOf_i1_heading_deg )                   | No      | number           | No         | -          | Compass heading of the screen's top edge as the head is mounted (landscape), degrees clockwise from north.    |
| - [heading_ref](#allOf_i1_heading_ref )                   | No      | enum (of string) | No         | -          | \`true\` north needs location access; otherwise magnetic north.                                               |
| - [heading_accuracy_deg](#allOf_i1_heading_accuracy_deg ) | No      | number           | No         | -          | Maximum heading error in degrees.                                                                             |
| - [sensor_time_s](#allOf_i1_sensor_time_s )               | No      | number           | No         | -          | Seconds since device boot (the clock of \`imu\`).                                                             |

### <a name="allOf_i1_pressure_kpa"></a>2.1. Property `Env > allOf > item 1 > pressure_kpa`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Air pressure in kilopascals.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_relative_altitude_m"></a>2.2. Property `Env > allOf > item 1 > relative_altitude_m`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Change in altitude in metres since the barometer started (this subscription or an earlier one still running).

### <a name="allOf_i1_magnetic_field_ut"></a>2.3. Property `Env > allOf > item 1 > magnetic_field_ut`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of number` |
| **Required** | No                |

**Description:** Raw magnetic field in microtesla, device frame; includes the device's own bias.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 3                  |
| **Max items**        | 3                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be                              | Description |
| ------------------------------------------------------------ | ----------- |
| [magnetic_field_ut items](#allOf_i1_magnetic_field_ut_items) | -           |

#### <a name="allOf_i1_magnetic_field_ut_items"></a>2.3.1. Env > allOf > item 1 > magnetic_field_ut > magnetic_field_ut items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

### <a name="allOf_i1_heading_deg"></a>2.4. Property `Env > allOf > item 1 > heading_deg`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Compass heading of the screen's top edge as the head is mounted (landscape), degrees clockwise from north.

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; 0   |
| **Maximum**  | &le; 360 |

### <a name="allOf_i1_heading_ref"></a>2.5. Property `Env > allOf > item 1 > heading_ref`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** `true` north needs location access; otherwise magnetic north.

Must be one of:
* "true"
* "magnetic"

### <a name="allOf_i1_heading_accuracy_deg"></a>2.6. Property `Env > allOf > item 1 > heading_accuracy_deg`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Maximum heading error in degrees.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_sensor_time_s"></a>2.7. Property `Env > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Seconds since device boot (the clock of `imu`).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Env > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"env"`

----------------------------------------------------------------------------------------------------------------------------
