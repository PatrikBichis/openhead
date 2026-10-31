# FaceSetTheme

**Title:** FaceSetTheme

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Switch the face to an installed theme. Unknown names give `invalid_params`.

| Property                           | Pattern | Type    | Deprecated | Definition                           | Title/Description                                            |
| ---------------------------------- | ------- | ------- | ---------- | ------------------------------------ | ------------------------------------------------------------ |
| + [type](#type )                   | No      | string  | No         | -                                    | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )                       | No      | integer | No         | -                                    | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )                     | No      | integer | No         | -                                    | Per-connection, per-direction counter, starting at 0.        |
| + [id](#id )                       | No      | string  | No         | -                                    | Client-chosen id, echoed in the reply.                       |
| + [name](#name )                   | No      | string  | No         | In ../common.json#/$defs/name        | Lower-case identifier used for themes and emotions.          |
| - [transition_ms](#transition_ms ) | No      | integer | No         | In ../common.json#/$defs/duration_ms | Cross-fade time. Default 300.                                |

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

## <a name="name"></a>5. Property `FaceSetTheme > name`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | Yes                        |
| **Defined in** | ../common.json#/$defs/name |

**Description:** Lower-case identifier used for themes and emotions.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

## <a name="transition_ms"></a>6. Property `FaceSetTheme > transition_ms`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `integer`                         |
| **Required**   | No                                |
| **Defined in** | ../common.json#/$defs/duration_ms |

**Description:** Cross-fade time. Default 300.

| Restrictions |             |
| ------------ | ----------- |
| **Minimum**  | &ge; 0      |
| **Maximum**  | &le; 600000 |

----------------------------------------------------------------------------------------------------------------------------
