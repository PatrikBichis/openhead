# Subscribe

**Title:** Subscribe

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Open a stream. The device clamps `rate_hz` to what it supports and returns the actual rate. Subscribing again to the same topic replaces the earlier subscription.

| Property               | Pattern | Type             | Deprecated | Definition                     | Title/Description                                                                                                                                                                                                                                |
| ---------------------- | ------- | ---------------- | ---------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| + [type](#type )       | No      | string           | No         | -                              | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.                                                                                                                                                                                     |
| + [ts](#ts )           | No      | integer          | No         | -                              | Sender clock in milliseconds since the Unix epoch.                                                                                                                                                                                               |
| + [seq](#seq )         | No      | integer          | No         | -                              | Per-connection, per-direction counter, starting at 0.                                                                                                                                                                                            |
| + [id](#id )           | No      | string           | No         | -                              | Client-chosen id, echoed in the reply.                                                                                                                                                                                                           |
| + [topic](#topic )     | No      | enum (of string) | No         | In ../common.json#/$defs/topic | Subscribable stream. \`faces\` needs mode \`capture\` or \`sensing\`, \`pose\` needs \`sensing\`; \`gps\` asks for location access and \`env\` for Motion & Fitness access on first use; \`speech\` carries speaking and listening events (0.4). |
| - [rate_hz](#rate_hz ) | No      | number           | No         | -                              | Requested rate. Ignored for event-driven topics such as \`log\`.                                                                                                                                                                                 |
| - [fields](#fields )   | No      | array of string  | No         | -                              | Only send these payload fields. Omit for all.                                                                                                                                                                                                    |

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

## <a name="topic"></a>5. Property `Subscribe > topic`

|                |                             |
| -------------- | --------------------------- |
| **Type**       | `enum (of string)`          |
| **Required**   | Yes                         |
| **Defined in** | ../common.json#/$defs/topic |

**Description:** Subscribable stream. `faces` needs mode `capture` or `sensing`, `pose` needs `sensing`; `gps` asks for location access and `env` for Motion & Fitness access on first use; `speech` carries speaking and listening events (0.4).

Must be one of:
* "imu"
* "status"
* "log"
* "faces"
* "pose"
* "gps"
* "env"
* "speech"

## <a name="rate_hz"></a>6. Property `Subscribe > rate_hz`

|              |          |
| ------------ | -------- |
| **Type**     | `number` |
| **Required** | No       |

**Description:** Requested rate. Ignored for event-driven topics such as `log`.

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &gt; 0    |
| **Maximum**  | &le; 1000 |

## <a name="fields"></a>7. Property `Subscribe > fields`

|              |                   |
| ------------ | ----------------- |
| **Type**     | `array of string` |
| **Required** | No                |

**Description:** Only send these payload fields. Omit for all.

|                      | Array restrictions |
| -------------------- | ------------------ |
| **Min items**        | N/A                |
| **Max items**        | N/A                |
| **Items unicity**    | True               |
| **Additional items** | False              |
| **Tuple validation** | See below          |

| Each item of this array must be | Description |
| ------------------------------- | ----------- |
| [fields items](#fields_items)   | -           |

### <a name="fields_items"></a>7.1. Subscribe > fields > fields items

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

----------------------------------------------------------------------------------------------------------------------------
