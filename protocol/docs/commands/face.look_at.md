# FaceLookAt

**Title:** FaceLookAt

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Point the gaze. `screen`: `x`, `y` in [-1, 1] with origin at the screen centre, +x right, +y up. `head`: `yaw`, `pitch` in degrees in the head frame, +yaw left, +pitch up. The world frame needs pose and arrives in 0.2.

| Property                       | Pattern | Type             | Deprecated | Definition                           | Title/Description                                                                   |
| ------------------------------ | ------- | ---------------- | ---------- | ------------------------------------ | ----------------------------------------------------------------------------------- |
| + [type](#type )               | No      | const            | No         | -                                    | -                                                                                   |
| + [frame](#frame )             | No      | enum (of string) | No         | -                                    | -                                                                                   |
| - [x](#x )                     | No      | number           | No         | In ../common.json#/$defs/signed_unit | -                                                                                   |
| - [y](#y )                     | No      | number           | No         | Same as [x](#x )                     | -                                                                                   |
| - [yaw](#yaw )                 | No      | number           | No         | -                                    | -                                                                                   |
| - [pitch](#pitch )             | No      | number           | No         | -                                    | -                                                                                   |
| - [duration_ms](#duration_ms ) | No      | integer          | No         | In ../common.json#/$defs/duration_ms | Hold the gaze, then return to idle motion. Omit to hold until the next \`look_at\`. |

| All of(Requirement)  |
| -------------------- |
| [Command](#allOf_i0) |
| [item 1](#allOf_i1)  |

## <a name="allOf_i0"></a>1. Property `FaceLookAt > allOf > Command`

**Title:** Command

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | ../command.json  |

**Description:** Base for commands. Every command is answered with `ack` or `error` carrying the same `id`.

| Property                  | Pattern | Type    | Deprecated | Definition | Title/Description                                            |
| ------------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#allOf_i0_type ) | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#allOf_i0_ts )     | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#allOf_i0_seq )   | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| + [id](#allOf_i0_id )     | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                       |

### <a name="allOf_i0_type"></a>1.1. Property `FaceLookAt > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `FaceLookAt > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `FaceLookAt > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_id"></a>1.4. Property `FaceLookAt > allOf > Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="allOf_i1"></a>2. Property `FaceLookAt > allOf > item 1`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

### <a name="autogenerated_heading_2"></a>2.1. If (frame = "screen")

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

#### <a name="autogenerated_heading_3"></a>2.1.1. The following properties are required
* x
* y

### <a name="autogenerated_heading_4"></a>2.2. Else (i.e.  frame != "screen")

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

#### <a name="autogenerated_heading_5"></a>2.2.1. The following properties are required
* yaw
* pitch

## <a name="type"></a>3. Property `FaceLookAt > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"face.look_at"`

## <a name="frame"></a>4. Property `FaceLookAt > frame`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | Yes                |

Must be one of:
* "screen"
* "head"

## <a name="x"></a>5. Property `FaceLookAt > x`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `number`                          |
| **Required**   | No                                |
| **Defined in** | ../common.json#/$defs/signed_unit |

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; -1 |
| **Maximum**  | &le; 1  |

## <a name="y"></a>6. Property `FaceLookAt > y`

|                        |          |
| ---------------------- | -------- |
| **Type**               | `number` |
| **Required**           | No       |
| **Same definition as** | [x](#x)  |

## <a name="yaw"></a>7. Property `FaceLookAt > yaw`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; -90 |
| **Maximum**  | &le; 90  |

## <a name="pitch"></a>8. Property `FaceLookAt > pitch`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; -90 |
| **Maximum**  | &le; 90  |

## <a name="duration_ms"></a>9. Property `FaceLookAt > duration_ms`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `integer`                         |
| **Required**   | No                                |
| **Defined in** | ../common.json#/$defs/duration_ms |

**Description:** Hold the gaze, then return to idle motion. Omit to hold until the next `look_at`.

| Restrictions |             |
| ------------ | ----------- |
| **Minimum**  | &ge; 0      |
| **Maximum**  | &le; 600000 |

----------------------------------------------------------------------------------------------------------------------------
