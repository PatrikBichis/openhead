# Faces

**Title:** Faces

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** People in front of the head, up to 15 Hz while mode is `capture` (front camera, several faces, with `box`) or `sensing` (ARKit, one face, no `box`). Angles are in the head frame like `face.look_at`: +bearing to the head's left, +elevation up, in degrees. An empty list means nobody is seen. Every payload field is present unless the subscription named `fields`.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Faces > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Faces > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Faces > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Faces > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Faces > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type             | Deprecated | Definition | Title/Description |
| ------------------------------------------- | ------- | ---------------- | ---------- | ---------- | ----------------- |
| - [faces](#allOf_i1_faces )                 | No      | array            | No         | -          | -                 |
| - [source](#allOf_i1_source )               | No      | enum (of string) | No         | -          | -                 |
| - [sensor_time_s](#allOf_i1_sensor_time_s ) | No      | number           | No         | -          | -                 |

### <a name="allOf_i1_faces"></a>2.1. Property `Faces > allOf > item 1 > faces`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 16                 |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [face](#allOf_i1_faces_items)   | -           |

#### <a name="allOf_i1_faces_items"></a>2.1.1. Faces > allOf > item 1 > faces > face

|                           |              |
| ------------------------- | ------------ |
| **Type**                  | `object`     |
| **Required**              | No           |
| **Additional properties** | Not allowed  |
| **Defined in**            | #/$defs/face |

| Property                                          | Pattern | Type    | Deprecated | Definition     | Title/Description                                                                         |
| ------------------------------------------------- | ------- | ------- | ---------- | -------------- | ----------------------------------------------------------------------------------------- |
| + [id](#allOf_i1_faces_items_id )                 | No      | integer | No         | -              | Stable while the face stays in view.                                                      |
| + [bearing](#allOf_i1_faces_items_bearing )       | No      | number  | No         | -              | Degrees, + to the head's left.                                                            |
| + [elevation](#allOf_i1_faces_items_elevation )   | No      | number  | No         | -              | Degrees, + up.                                                                            |
| + [size](#allOf_i1_faces_items_size )             | No      | number  | No         | -              | Face width as a share of the camera's field of view: bigger is closer.                    |
| - [distance_m](#allOf_i1_faces_items_distance_m ) | No      | number  | No         | -              | Metres, when the depth camera measures it (\`sensing\`).                                  |
| + [confidence](#allOf_i1_faces_items_confidence ) | No      | number  | No         | -              | -                                                                                         |
| - [box](#allOf_i1_faces_items_box )               | No      | object  | No         | In #/$defs/box | Where the face is in the camera view as shown on screen, normalised 0-1, origin top-left. |
| - [locked](#allOf_i1_faces_items_locked )         | No      | boolean | No         | -              | The face the HUD and \`look_at {frame: face}\` follow.                                    |

##### <a name="allOf_i1_faces_items_id"></a>2.1.1.1. Property `Faces > allOf > item 1 > faces > faces items > id`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Stable while the face stays in view.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

##### <a name="allOf_i1_faces_items_bearing"></a>2.1.1.2. Property `Faces > allOf > item 1 > faces > faces items > bearing`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

**Description:** Degrees, + to the head's left.

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; -90 |
| **Maximum**  | &le; 90  |

##### <a name="allOf_i1_faces_items_elevation"></a>2.1.1.3. Property `Faces > allOf > item 1 > faces > faces items > elevation`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

**Description:** Degrees, + up.

| Restrictions |          |
| ------------ | -------- |
| **Minimum**  | &ge; -90 |
| **Maximum**  | &le; 90  |

##### <a name="allOf_i1_faces_items_size"></a>2.1.1.4. Property `Faces > allOf > item 1 > faces > faces items > size`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

**Description:** Face width as a share of the camera's field of view: bigger is closer.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

##### <a name="allOf_i1_faces_items_distance_m"></a>2.1.1.5. Property `Faces > allOf > item 1 > faces > faces items > distance_m`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Metres, when the depth camera measures it (`sensing`).

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

##### <a name="allOf_i1_faces_items_confidence"></a>2.1.1.6. Property `Faces > allOf > item 1 > faces > faces items > confidence`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

##### <a name="allOf_i1_faces_items_box"></a>2.1.1.7. Property `Faces > allOf > item 1 > faces > faces items > box`

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |
| **Defined in**            | #/$defs/box |

**Description:** Where the face is in the camera view as shown on screen, normalised 0-1, origin top-left.

| Property                            | Pattern | Type   | Deprecated | Definition | Title/Description |
| ----------------------------------- | ------- | ------ | ---------- | ---------- | ----------------- |
| + [x](#allOf_i1_faces_items_box_x ) | No      | number | No         | -          | -                 |
| + [y](#allOf_i1_faces_items_box_y ) | No      | number | No         | -          | -                 |
| + [w](#allOf_i1_faces_items_box_w ) | No      | number | No         | -          | -                 |
| + [h](#allOf_i1_faces_items_box_h ) | No      | number | No         | -          | -                 |

###### <a name="allOf_i1_faces_items_box_x"></a>2.1.1.7.1. Property `Faces > allOf > item 1 > faces > faces items > box > x`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

###### <a name="allOf_i1_faces_items_box_y"></a>2.1.1.7.2. Property `Faces > allOf > item 1 > faces > faces items > box > y`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

###### <a name="allOf_i1_faces_items_box_w"></a>2.1.1.7.3. Property `Faces > allOf > item 1 > faces > faces items > box > w`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

###### <a name="allOf_i1_faces_items_box_h"></a>2.1.1.7.4. Property `Faces > allOf > item 1 > faces > faces items > box > h`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

##### <a name="allOf_i1_faces_items_locked"></a>2.1.1.8. Property `Faces > allOf > item 1 > faces > faces items > locked`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

**Description:** The face the HUD and `look_at {frame: face}` follow.

### <a name="allOf_i1_source"></a>2.2. Property `Faces > allOf > item 1 > source`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

Must be one of:
* "vision"
* "arkit"
* "sim"

### <a name="allOf_i1_sensor_time_s"></a>2.3. Property `Faces > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Faces > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"faces"`

----------------------------------------------------------------------------------------------------------------------------
