# DepthSample

**Title:** DepthSample

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Distance from the back camera to what is at given points of its view, from the LiDAR depth map (0.5, optional). Needs capability `lidar` and mode `sensing`; otherwise `unsupported`. Points are normalised 0-1 in the `camera` frame from the back camera (origin top-left).

| Property             | Pattern | Type    | Deprecated | Definition | Title/Description                                            |
| -------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#type )     | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )         | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )       | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| + [id](#id )         | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                       |
| + [points](#points ) | No      | array   | No         | -          | -                                                            |

## <a name="type"></a>1. Property `Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

## <a name="ts"></a>2. Property `Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="seq"></a>3. Property `Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

## <a name="id"></a>4. Property `Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="points"></a>5. Property `DepthSample > points`

|              |         |
| ------------ | ------- |
| **Type**     | `array` |
| **Required** | Yes     |

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | 1                  |
| **Max items**        | 16                 |
| **Items unicity**    | False              |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [point](#points_items)          | -           |

### <a name="points_items"></a>5.1. DepthSample > points > point

|                           |               |
| ------------------------- | ------------- |
| **Type**                  | `object`      |
| **Required**              | No            |
| **Additional properties** | Not allowed   |
| **Defined in**            | #/$defs/point |

| Property                | Pattern | Type   | Deprecated | Definition | Title/Description |
| ----------------------- | ------- | ------ | ---------- | ---------- | ----------------- |
| + [x](#points_items_x ) | No      | number | No         | -          | -                 |
| + [y](#points_items_y ) | No      | number | No         | -          | -                 |

#### <a name="points_items_x"></a>5.1.1. Property `DepthSample > points > points items > x`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

#### <a name="points_items_y"></a>5.1.2. Property `DepthSample > points > points items > y`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | Yes      |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

----------------------------------------------------------------------------------------------------------------------------
