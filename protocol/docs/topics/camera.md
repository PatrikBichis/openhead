# Camera

**Title:** Camera

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** What the head's camera sees, as small JPEG frames for a viewer (0.5): the front camera in mode `capture`, the back camera in `sensing`, nothing in `idle`. Up to 10 Hz; `subscribe.max_px` sets the longest side (default 320, 80-640). Frames go only to paired clients that subscribe, are never stored, and the phone shows that someone is watching while any subscription is open. Every payload field is present unless the subscription named `fields`.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Camera > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Camera > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Camera > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Camera > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Camera > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type             | Deprecated | Definition | Title/Description                                                          |
| ------------------------------------------- | ------- | ---------------- | ---------- | ---------- | -------------------------------------------------------------------------- |
| - [jpeg](#allOf_i1_jpeg )                   | No      | string           | No         | -          | The frame, base64 JPEG, upright as the head is mounted (landscape).        |
| - [width](#allOf_i1_width )                 | No      | integer          | No         | -          | -                                                                          |
| - [height](#allOf_i1_height )               | No      | integer          | No         | -          | -                                                                          |
| - [source](#allOf_i1_source )               | No      | enum (of string) | No         | -          | \`front\` in \`capture\`, \`back\` (ARKit's camera) in \`sensing\`.        |
| - [frame](#allOf_i1_frame )                 | No      | integer          | No         | -          | Counts frames sent on this subscription.                                   |
| - [sensor_time_s](#allOf_i1_sensor_time_s ) | No      | number           | No         | -          | When the camera took it, seconds since device boot (the clock of \`imu\`). |

### <a name="allOf_i1_jpeg"></a>2.1. Property `Camera > allOf > item 1 > jpeg`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** The frame, base64 JPEG, upright as the head is mounted (landscape).

| Restrictions   |        |
| -------------- | ------ |
| **Max length** | 200000 |

### <a name="allOf_i1_width"></a>2.2. Property `Camera > allOf > item 1 > width`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; 1   |
| **Maximum**  | &le; 640 |

### <a name="allOf_i1_height"></a>2.3. Property `Camera > allOf > item 1 > height`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; 1   |
| **Maximum**  | &le; 640 |

### <a name="allOf_i1_source"></a>2.4. Property `Camera > allOf > item 1 > source`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** `front` in `capture`, `back` (ARKit's camera) in `sensing`.

Must be one of:
* "front"
* "back"
* "sim"

### <a name="allOf_i1_frame"></a>2.5. Property `Camera > allOf > item 1 > frame`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

**Description:** Counts frames sent on this subscription.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i1_sensor_time_s"></a>2.6. Property `Camera > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** When the camera took it, seconds since device boot (the clock of `imu`).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Camera > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"camera"`

----------------------------------------------------------------------------------------------------------------------------
