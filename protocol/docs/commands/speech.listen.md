# SpeechListen

**Title:** SpeechListen

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            |                  |

**Description:** Listen with the head's microphone and turn speech into text, on the device when it can. What is heard comes on the `speech` topic: `partial` while someone talks, `heard` when they pause. Asks for microphone and speech recognition permission the first time (`unsupported` if refused). With `auto_expressions` (default true) the face looks attentive while someone talks and thoughtful after they finish, until the next `speech.say`.

| Property                                 | Pattern | Type    | Deprecated | Definition | Title/Description                                             |
| ---------------------------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------- |
| + [type](#type )                         | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`.  |
| + [ts](#ts )                             | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.            |
| + [seq](#seq )                           | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.         |
| + [id](#id )                             | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                        |
| + [on](#on )                             | No      | boolean | No         | -          | -                                                             |
| - [locale](#locale )                     | No      | string  | No         | -          | Language to recognise, e.g. \`en-US\` (default) or \`sv-SE\`. |
| - [auto_expressions](#auto_expressions ) | No      | boolean | No         | -          | Attentive while hearing, thinking after; default true.        |
| - [silence_ms](#silence_ms )             | No      | integer | No         | -          | Silence that ends an utterance; default 1000.                 |

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

## <a name="on"></a>5. Property `SpeechListen > on`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | Yes       |

## <a name="locale"></a>6. Property `SpeechListen > locale`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Language to recognise, e.g. `en-US` (default) or `sv-SE`.

| Restrictions                      |                                                                                                                   |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z]{2}(-[A-Z]{2})?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%7B2%7D%28-%5BA-Z%5D%7B2%7D%29%3F%24) |

## <a name="auto_expressions"></a>7. Property `SpeechListen > auto_expressions`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

**Description:** Attentive while hearing, thinking after; default true.

## <a name="silence_ms"></a>8. Property `SpeechListen > silence_ms`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | No        |

**Description:** Silence that ends an utterance; default 1000.

| Restrictions |           |
| ------------ | --------- |
| **Minimum**  | &ge; 300  |
| **Maximum**  | &le; 5000 |

----------------------------------------------------------------------------------------------------------------------------
