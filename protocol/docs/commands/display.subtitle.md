# DisplaySubtitle

**Title:** DisplaySubtitle

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `combining`      |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

**Description:** Text on top of whatever is shown (face, image, video, web page): for a robot without a speaker, or to show an AI answer as it streams in. `replace` shows `text` alone, `append` adds it to what is shown (send tokens as they arrive), `clear` removes it. The newest three lines stay visible. With `mouth` the face's mouth moves with the text at reading pace, as if speaking.

| Property                       | Pattern | Type             | Deprecated | Definition                           | Title/Description                                                                                          |
| ------------------------------ | ------- | ---------------- | ---------- | ------------------------------------ | ---------------------------------------------------------------------------------------------------------- |
| + [type](#type )               | No      | const            | No         | -                                    | -                                                                                                          |
| - [text](#text )               | No      | string           | No         | -                                    | Plain text; a line break starts a new line. Required unless \`mode\` is \`clear\`.                         |
| - [mode](#mode )               | No      | enum (of string) | No         | -                                    | Default \`replace\`.                                                                                       |
| - [position](#position )       | No      | enum (of string) | No         | -                                    | Default \`bottom\`.                                                                                        |
| - [duration_ms](#duration_ms ) | No      | integer          | No         | In ../common.json#/$defs/duration_ms | Clear this long after the last update. Omit to hold until replaced or cleared.                             |
| - [mouth](#mouth )             | No      | boolean          | No         | -                                    | Move the mouth with the text at reading pace. Default false; ignored while \`face.envelope\` is streaming. |

| All of(Requirement)  |
| -------------------- |
| [Command](#allOf_i0) |
| [item 1](#allOf_i1)  |

## <a name="allOf_i0"></a>1. Property `DisplaySubtitle > allOf > Command`

**Title:** Command

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |
| **Defined in**            | ../command.json  |

**Description:** Base for commands. Every command is answered with `ack` or `error` carrying the same `id`.

| Property                  | Pattern | Type    | Deprecated | Definition | Title/Description                                            |
| ------------------------- | ------- | ------- | ---------- | ---------- | ------------------------------------------------------------ |
| + [type](#allOf_i0_type ) | No      | string  | No         | -          | Message type, e.g. \`hello\`, \`face.set_emotion\`, \`imu\`. |
| + [ts](#allOf_i0_ts )     | No      | integer | No         | -          | Sender clock in milliseconds since the Unix epoch.           |
| + [seq](#allOf_i0_seq )   | No      | integer | No         | -          | Per-connection, per-direction counter, starting at 0.        |
| + [id](#allOf_i0_id )     | No      | string  | No         | -          | Client-chosen id, echoed in the reply.                       |

### <a name="allOf_i0_type"></a>1.1. Property `DisplaySubtitle > allOf > Envelope > type`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Message type, e.g. `hello`, `face.set_emotion`, `imu`.

| Restrictions                      |                                                                                                                                           |
| --------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| **Must match regular expression** | ```^[a-z][a-z_]*(\.[a-z][a-z_]*)?$``` [Test](https://regex101.com/?regex=%5E%5Ba-z%5D%5Ba-z_%5D%2A%28%5C.%5Ba-z%5D%5Ba-z_%5D%2A%29%3F%24) |

### <a name="allOf_i0_ts"></a>1.2. Property `DisplaySubtitle > allOf > Envelope > ts`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Sender clock in milliseconds since the Unix epoch.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_seq"></a>1.3. Property `DisplaySubtitle > allOf > Envelope > seq`

|              |           |
| ------------ | --------- |
| **Type**     | `integer` |
| **Required** | Yes       |

**Description:** Per-connection, per-direction counter, starting at 0.

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |

### <a name="allOf_i0_id"></a>1.4. Property `DisplaySubtitle > allOf > Command > id`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | Yes      |

**Description:** Client-chosen id, echoed in the reply.

| Restrictions   |    |
| -------------- | -- |
| **Min length** | 1  |
| **Max length** | 64 |

## <a name="allOf_i1"></a>2. Property `DisplaySubtitle > allOf > item 1`

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

### <a name="autogenerated_heading_2"></a>2.1. Else (i.e.  mode != "clear")

|                           |                  |
| ------------------------- | ---------------- |
| **Type**                  | `object`         |
| **Required**              | No               |
| **Additional properties** | Any type allowed |

#### <a name="autogenerated_heading_3"></a>2.1.1. The following properties are required
* text

## <a name="type"></a>3. Property `DisplaySubtitle > type`

|              |         |
| ------------ | ------- |
| **Type**     | `const` |
| **Required** | Yes     |

Specific value: `"display.subtitle"`

## <a name="text"></a>4. Property `DisplaySubtitle > text`

|              |          |
| ------------ | -------- |
| **Type**     | `string` |
| **Required** | No       |

**Description:** Plain text; a line break starts a new line. Required unless `mode` is `clear`.

| Restrictions   |      |
| -------------- | ---- |
| **Max length** | 4000 |

## <a name="mode"></a>5. Property `DisplaySubtitle > mode`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Default `replace`.

Must be one of:
* "replace"
* "append"
* "clear"

## <a name="position"></a>6. Property `DisplaySubtitle > position`

|              |                    |
| ------------ | ------------------ |
| **Type**     | `enum (of string)` |
| **Required** | No                 |

**Description:** Default `bottom`.

Must be one of:
* "bottom"
* "top"

## <a name="duration_ms"></a>7. Property `DisplaySubtitle > duration_ms`

|                |                                   |
| -------------- | --------------------------------- |
| **Type**       | `integer`                         |
| **Required**   | No                                |
| **Defined in** | ../common.json#/$defs/duration_ms |

**Description:** Clear this long after the last update. Omit to hold until replaced or cleared.

| Restrictions |             |
| ------------ | ----------- |
| **Minimum**  | &ge; 0      |
| **Maximum**  | &le; 600000 |

## <a name="mouth"></a>8. Property `DisplaySubtitle > mouth`

|              |           |
| ------------ | --------- |
| **Type**     | `boolean` |
| **Required** | No        |

**Description:** Move the mouth with the text at reading pace. Default false; ignored while `face.envelope` is streaming.

----------------------------------------------------------------------------------------------------------------------------
