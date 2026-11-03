# Mesh

**Title:** Mesh

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** The room as triangle meshes from ARKit scene reconstruction (0.5, optional): only on devices with capability `scene_mesh` (LiDAR, Pro models) and only in mode `sensing`. Up to 1 Hz; each message carries the anchors that are new or changed since the last one and the ids of removed ones, so a client keeps a map by `id`. A device without LiDAR answers the subscription with `unsupported`.

| Property         | Pattern | Type  | Deprecated | Definition | Title/Description |
| ---------------- | ------- | ----- | ---------- | ---------- | ----------------- |
| + [type](#type ) | No      | const | No         | -          | -                 |

| All of(Requirement)   |
| --------------------- |
| [Envelope](#allOf_i0) |
| [fields](#allOf_i1)   |

## <a name="allOf_i0"></a>1. Property `Mesh > allOf > Envelope`

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

### <a name="allOf_i0_type"></a>1.1. Property `Mesh > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `Mesh > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `Mesh > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="allOf_i1"></a>2. Property `Mesh > allOf > fields`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | #/$defs/fields   |

| Property                                    | Pattern | Type            | Deprecated | Definition | Title/Description             |
| ------------------------------------------- | ------- | --------------- | ---------- | ---------- | ----------------------------- |
| - [anchors](#allOf_i1_anchors )             | No      | array           | No         | -          | New or changed anchors.       |
| - [removed](#allOf_i1_removed )             | No      | array of string | No         | -          | Ids of anchors ARKit dropped. |
| - [sensor_time_s](#allOf_i1_sensor_time_s ) | No      | number          | No         | -          | -                             |

### <a name="allOf_i1_anchors"></a>2.1. Property `Mesh > allOf > item 1 > anchors`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | No      |

**Description:** New or changed anchors.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | 64                 |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be   | Description |
| --------------------------------- | ----------- |
| [anchor](#allOf_i1_anchors_items) | -           |

#### <a name="allOf_i1_anchors_items"></a>2.1.1. Mesh > allOf > item 1 > anchors > anchor

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | No             |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/anchor |

| Property                                        | Pattern | Type            | Deprecated | Definition | Title/Description                                                                  |
| ----------------------------------------------- | ------- | --------------- | ---------- | ---------- | ---------------------------------------------------------------------------------- |
| + [id](#allOf_i1_anchors_items_id )             | No      | string          | No         | -          | -                                                                                  |
| + [position](#allOf_i1_anchors_items_position ) | No      | array of number | No         | -          | Anchor origin in the \`pose\` world frame, metres.                                 |
| + [q](#allOf_i1_anchors_items_q )               | No      | array of number | No         | -          | Anchor orientation in the world frame, unit quaternion [x, y, z, w] (as \`pose\`). |
| + [vertices](#allOf_i1_anchors_items_vertices ) | No      | string          | No         | -          | Little-endian float32 x, y, z per vertex, in the anchor frame, metres.             |
| + [faces](#allOf_i1_anchors_items_faces )       | No      | string          | No         | -          | Little-endian uint32 vertex indices, three per triangle.                           |

##### <a name="allOf_i1_anchors_items_id"></a>2.1.1.1. Property `Mesh > allOf > item 1 > anchors > anchors items > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

##### <a name="allOf_i1_anchors_items_position"></a>2.1.1.2. Property `Mesh > allOf > item 1 > anchors > anchors items > position`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of number` |
| **Required** | Yes               |

**Description:** Anchor origin in the `pose` world frame, metres.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 3                  |
| **Max items**        | 3                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be                          | Description |
| -------------------------------------------------------- | ----------- |
| [position items](#allOf_i1_anchors_items_position_items) | -           |

###### <a name="allOf_i1_anchors_items_position_items"></a>2.1.1.2.1. Mesh > allOf > item 1 > anchors > anchors items > position > position items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="allOf_i1_anchors_items_q"></a>2.1.1.3. Property `Mesh > allOf > item 1 > anchors > anchors items > q`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of number` |
| **Required** | Yes               |

**Description:** Anchor orientation in the world frame, unit quaternion [x, y, z, w] (as `pose`).

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 4                  |
| **Max items**        | 4                  |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be            | Description |
| ------------------------------------------ | ----------- |
| [q items](#allOf_i1_anchors_items_q_items) | -           |

###### <a name="allOf_i1_anchors_items_q_items"></a>2.1.1.3.1. Mesh > allOf > item 1 > anchors > anchors items > q > q items

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

##### <a name="allOf_i1_anchors_items_vertices"></a>2.1.1.4. Property `Mesh > allOf > item 1 > anchors > anchors items > vertices`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Little-endian float32 x, y, z per vertex, in the anchor frame, metres.

##### <a name="allOf_i1_anchors_items_faces"></a>2.1.1.5. Property `Mesh > allOf > item 1 > anchors > anchors items > faces`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Little-endian uint32 vertex indices, three per triangle.

### <a name="allOf_i1_removed"></a>2.2. Property `Mesh > allOf > item 1 > removed`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Ids of anchors ARKit dropped.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be          | Description |
| ---------------------------------------- | ----------- |
| [removed items](#allOf_i1_removed_items) | -           |

#### <a name="allOf_i1_removed_items"></a>2.2.1. Mesh > allOf > item 1 > removed > removed items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

### <a name="allOf_i1_sensor_time_s"></a>2.3. Property `Mesh > allOf > item 1 > sensor_time_s`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="type"></a>3. Property `Mesh > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"mesh"`

----------------------------------------------------------------------------------------------------------------------------
