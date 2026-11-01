# Gps

**Title:** Gps

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Where the head is on Earth, up to 1 Hz (CoreLocation: GNSS where the device has it, otherwise Wi-Fi). Sent only after the user allows location access; the first subscription asks. WGS 84. Every payload field is present unless the subscription named `fields`; `alt_m`, `v_accuracy_m`, `speed_m_s` and `course_deg` are left out when unknown.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Gps > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Gps > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Gps > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Gps > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Gps > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type   | Deprecated | Definition | Title/Description                                                         |
| ------------------------------------------- | ------- | ------ | ---------- | ---------- | ------------------------------------------------------------------------- |
| - [lat](#allOf_i1_lat )                     | No      | number | No         | -          | Latitude in degrees, + north.                                             |
| - [lon](#allOf_i1_lon )                     | No      | number | No         | -          | Longitude in degrees, + east.                                             |
| - [alt_m](#allOf_i1_alt_m )                 | No      | number | No         | -          | Altitude above mean sea level in metres.                                  |
| - [h_accuracy_m](#allOf_i1_h_accuracy_m )   | No      | number | No         | -          | Radius of horizontal uncertainty in metres (68 %).                        |
| - [v_accuracy_m](#allOf_i1_v_accuracy_m )   | No      | number | No         | -          | Vertical uncertainty in metres.                                           |
| - [speed_m_s](#allOf_i1_speed_m_s )         | No      | number | No         | -          | Ground speed in m/s.                                                      |
| - [course_deg](#allOf_i1_course_deg )       | No      | number | No         | -          | Direction of travel, degrees clockwise from true north.                   |
| - [sensor_time_s](#allOf_i1_sensor_time_s ) | No      | number | No         | -          | When the fix was taken, seconds since device boot (the clock of \`imu\`). |

### <a name="allOf_i1_lat"></a>2.1. Property `Gps > allOf > item 1 > lat`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Latitude in degrees, + north.

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; -90 |
| **Maximum**  | &le; 90  |

### <a name="allOf_i1_lon"></a>2.2. Property `Gps > allOf > item 1 > lon`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Longitude in degrees, + east.

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; -180 |
| **Maximum**  | &le; 180  |

### <a name="allOf_i1_alt_m"></a>2.3. Property `Gps > allOf > item 1 > alt_m`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Altitude above mean sea level in metres.

### <a name="allOf_i1_h_accuracy_m"></a>2.4. Property `Gps > allOf > item 1 > h_accuracy_m`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Radius of horizontal uncertainty in metres (68 %).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_v_accuracy_m"></a>2.5. Property `Gps > allOf > item 1 > v_accuracy_m`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Vertical uncertainty in metres.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_speed_m_s"></a>2.6. Property `Gps > allOf > item 1 > speed_m_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Ground speed in m/s.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_course_deg"></a>2.7. Property `Gps > allOf > item 1 > course_deg`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Direction of travel, degrees clockwise from true north.

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; 0   |
| **Maximum**  | &le; 360 |

### <a name="allOf_i1_sensor_time_s"></a>2.8. Property `Gps > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** When the fix was taken, seconds since device boot (the clock of `imu`).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Gps > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"gps"`

----------------------------------------------------------------------------------------------------------------------------
