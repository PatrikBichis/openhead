# Imu

**Title:** Imu

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Inertial sample, up to 100 Hz. Right-handed frame: in `device` frame +x is right, +y is up and +z points out of the screen (portrait). `mount` applies the `mount_offset` setting. Every payload field is present unless the subscription named `fields`; then only those are.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Imu > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Imu > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Imu > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Imu > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Imu > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type             | Deprecated | Definition                      | Title/Description                                                                                                                |
| ------------------------------------------- | ------- | ---------------- | ---------- | ------------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| - [q](#allOf_i1_q )                         | No      | array of number  | No         | -                               | Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference frame.                                      |
| - [gyro](#allOf_i1_gyro )                   | No      | array of number  | No         | In #/$defs/vec3                 | Angular rate in rad/s.                                                                                                           |
| - [accel](#allOf_i1_accel )                 | No      | array of number  | No         | Same as [gyro](#allOf_i1_gyro ) | Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS CoreMotion reports the opposite sign.) |
| - [frame](#allOf_i1_frame )                 | No      | enum (of string) | No         | -                               | -                                                                                                                                |
| - [sensor_time_s](#allOf_i1_sensor_time_s ) | No      | number           | No         | -                               | Sensor timestamp in seconds since device boot, for precise intervals between samples.                                            |

### <a name="allOf_i1_q"></a>2.1. Property `Imu > allOf > item 1 > q`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of number` |
| **Required** | No                |

**Description:** Orientation as unit quaternion [x, y, z, w], relative to a gravity-aligned reference frame.

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

#### <a name="allOf_i1_q_items"></a>2.1.1. Imu > allOf > item 1 > q > q items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; -1 |
| **Maximum**  | &le; 1  |

### <a name="allOf_i1_gyro"></a>2.2. Property `Imu > allOf > item 1 > gyro`

|                |                   |
| -------------- | ----------------- |
| **Type**       | `array of number` |
| **Required**   | No                |
| **Defined in** | #/$defs/vec3      |

**Description:** Angular rate in rad/s.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 3                  |
| **Max items**        | 3                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be    | Description |
| ---------------------------------- | ----------- |
| [gyro items](#allOf_i1_gyro_items) | -           |

#### <a name="allOf_i1_gyro_items"></a>2.2.1. Imu > allOf > item 1 > gyro > gyro items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

### <a name="allOf_i1_accel"></a>2.3. Property `Imu > allOf > item 1 > accel`

|                        |                        |
| ---------------------- | ---------------------- |
| **Type**               | `array of number`      |
| **Required**           | No                     |
| **Same definition as** | [gyro](#allOf_i1_gyro) |

**Description:** Specific force in m/s^2, as a ROS IMU reports it: at rest upright about +9.81 on +y. (iOS CoreMotion reports the opposite sign.)

### <a name="allOf_i1_frame"></a>2.4. Property `Imu > allOf > item 1 > frame`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "device"
* "mount"

### <a name="allOf_i1_sensor_time_s"></a>2.5. Property `Imu > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Sensor timestamp in seconds since device boot, for precise intervals between samples.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Imu > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"imu"`

----------------------------------------------------------------------------------------------------------------------------
