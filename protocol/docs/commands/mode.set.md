# ModeSet

**Title:** ModeSet

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Choose who owns the cameras. In 0.1 only `idle` is accepted; other modes give `unsupported`.

| Property         | Pattern | Type             | Deprecated | Definition                    | Title/Description                                            |
| ---------------- | ------- | ---------------- | ---------- | ----------------------------- | ------------------------------------------------------------ |
| + [type](#type ) | No      | string           | No         | -                             | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )     | No      | integer          | No         | -                             | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )   | No      | integer          | No         | -                             | Per-connection, per-direction counter, starting at 0.        |
| + [id](#id )     | No      | string           | No         | -                             | Client-chosen id, echoed in the reply.                       |
| + [mode](#mode ) | No      | enum (of string) | No         | In ../common.json#/$defs/mode | Camera ownership mode. Only \`idle\` is supported in 0.1.    |

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

## <a name="mode"></a>5. Property `ModeSet > mode`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `enum (of string)`         |
| **Required**   | Yes                        |
| **Defined in** | ../common.json#/$defs/mode |

**Description:** Camera ownership mode. Only `idle` is supported in 0.1.

Must be one of:
* "idle"
* "sensing"
* "capture"

----------------------------------------------------------------------------------------------------------------------------
