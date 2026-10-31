# Pose

**Title:** Pose

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Where the head is, up to 60 Hz while mode is `sensing` (ARKit world tracking). World frame: origin where tracking started, +y up (against gravity), +x and +z horizontal; position in metres. `q` turns the device frame of `imu` into the world frame ([x, y, z, w]). Every payload field is present unless the subscription named `fields`.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Pose > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Pose > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Pose > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Pose > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Pose > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                        | Pattern | Type             | Deprecated | Definition | Title/Description                                          |
| ----------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ---------------------------------------------------------- |
| - [position](#allOf_i1_position )               | No      | array of number  | No         | -          | Metres in the world frame.                                 |
| - [q](#allOf_i1_q )                             | No      | array of number  | No         | -          | Unit quaternion [x, y, z, w], device frame to world frame. |
| - [tracking_state](#allOf_i1_tracking_state )   | No      | enum (of string) | No         | -          | -                                                          |
| - [tracking_reason](#allOf_i1_tracking_reason ) | No      | enum (of string) | No         | -          | Why tracking is \`limited\`.                               |
| - [frame](#allOf_i1_frame )                     | No      | enum (of string) | No         | -          | -                                                          |
| - [sensor_time_s](#allOf_i1_sensor_time_s )     | No      | number           | No         | -          | -                                                          |

### <a name="allOf_i1_position"></a>2.1. Property `Pose > allOf > item 1 > position`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of number` |
| **Required** | No                |

**Description:** Metres in the world frame.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 3                  |
| **Max items**        | 3                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be            | Description |
| ------------------------------------------ | ----------- |
| [position items](#allOf_i1_position_items) | -           |

#### <a name="allOf_i1_position_items"></a>2.1.1. Pose > allOf > item 1 > position > position items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

### <a name="allOf_i1_q"></a>2.2. Property `Pose > allOf > item 1 > q`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of number` |
| **Required** | No                |

**Description:** Unit quaternion [x, y, z, w], device frame to world frame.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 4                  |
| **Max items**        | 4                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [q items](#allOf_i1_q_items)    | -           |

#### <a name="allOf_i1_q_items"></a>2.2.1. Pose > allOf > item 1 > q > q items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; -1 |
| **Maximum**  | &le; 1  |

### <a name="allOf_i1_tracking_state"></a>2.3. Property `Pose > allOf > item 1 > tracking_state`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "normal"
* "limited"
* "not_available"

### <a name="allOf_i1_tracking_reason"></a>2.4. Property `Pose > allOf > item 1 > tracking_reason`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Why tracking is `limited`.

Must be one of:
* "initializing"
* "excessive_motion"
* "insufficient_features"
* "relocalizing"

### <a name="allOf_i1_frame"></a>2.5. Property `Pose > allOf > item 1 > frame`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "world"

### <a name="allOf_i1_sensor_time_s"></a>2.6. Property `Pose > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Pose > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"pose"`

----------------------------------------------------------------------------------------------------------------------------
