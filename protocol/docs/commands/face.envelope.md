# FaceEnvelope

**Title:** FaceEnvelope

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Mouth envelope from the host's speech audio, sent as a stream at 20-30 Hz while speaking. Not a command: no `id` and no reply. The face decays to closed if no update arrives for 200 ms.

| Property           | Pattern | Type    | Deprecated | Definition                    | Title/Description                                            |
| ------------------ | ------- | ------- | ---------- | ----------------------------- | ------------------------------------------------------------ |
| + [type](#type )   | No      | string  | No         | -                             | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#ts )       | No      | integer | No         | -                             | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#seq )     | No      | integer | No         | -                             | Per-connection, per-direction counter, starting at 0.        |
| + [level](#level ) | No      | number  | No         | In ../common.json#/$defs/unit | -                                                            |

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

## <a name="level"></a>4. Property `FaceEnvelope > level`

|                |                            |
| -------------- | -------------------------- |
| **Type**       | `number`                   |
| **Required**   | Yes                        |
| **Defined in** | ../common.json#/$defs/unit |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

----------------------------------------------------------------------------------------------------------------------------
