# FaceSetEmotion

**Title:** FaceSetEmotion

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Blend towards an emotion. Shared names: neutral, happy, curious, thinking, surprised, sad, angry, sleepy, scared, mischievous; themes may add extras (see `face.list`). Names the theme lacks fall back to `neutral` with a warning in the log.

| Property                       | Pattern | Type             | Deprecated | Definition                           | Title/Description                                                                 |
| ------------------------------ | ------- | ---------------- | ---------- | ------------------------------------ | --------------------------------------------------------------------------------- |
| + [type](#type )               | No      | string           | No         | -                                    | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.                      |
| + [ts](#ts )                   | No      | integer          | No         | -                                    | Sender clock in milliseconds since the Unix epoch.                                |
| + [seq](#seq )                 | No      | integer          | No         | -                                    | Per-connection, per-direction counter, starting at 0.                             |
| + [id](#id )                   | No      | string           | No         | -                                    | Client-chosen id, echoed in the reply.                                            |
| + [name](#name )               | No      | string           | No         | In ../common.json#/$defs/name        | Lower-case identifier used for themes and emotions.                               |
| - [intensity](#intensity )     | No      | number           | No         | In ../common.json#/$defs/unit        | Weight of the emotion. Default 1.                                                 |
| - [duration_ms](#duration_ms ) | No      | integer          | No         | In ../common.json#/$defs/duration_ms | Return to the resting emotion after this time. Omit to hold.                      |
| - [blend](#blend )             | No      | enum (of string) | No         | -                                    | \`replace\` fades out other emotions; \`add\` layers on top. Default \`replace\`. |

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

## <a name="name"></a>5. Property `FaceSetEmotion > name`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `string`                   |
| **Required**   | Yes                        |
| **Defined in** | ../common.json#/$defs/name |

**Description:** Lower-case identifier used for themes and emotions.

| Restrictions                      |                                                                                                             |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z0-9_-]{0,31}$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z0-9_-%5D%7B0%2C31%7D%24) |

## <a name="intensity"></a>6. Property `FaceSetEmotion > intensity`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `number`                   |
| **Required**   | No                         |
| **Defined in** | ../common.json#/$defs/unit |

**Description:** Weight of the emotion. Default 1.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

## <a name="duration_ms"></a>7. Property `FaceSetEmotion > duration_ms`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `integer`                         |
| **Required**   | No                                |
| **Defined in** | ../common.json#/$defs/duration_ms |

**Description:** Return to the resting emotion after this time. Omit to hold.

| Restrictions |             |
| ------------ | ----------- |
| **Minimum**  | &ge; 0      |
| **Maximum**  | &le; 600000 |

## <a name="blend"></a>8. Property `FaceSetEmotion > blend`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** `replace` fades out other emotions; `add` layers on top. Default `replace`.

Must be one of:
* "replace"
* "add"

----------------------------------------------------------------------------------------------------------------------------
