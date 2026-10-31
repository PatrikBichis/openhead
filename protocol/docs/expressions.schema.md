# Expressions

**Title:** Expressions

|                           |             |
| ------------------------- | ----------- |
| **Type**                  | `object`    |
| **Required**              | No          |
| **Additional properties** | Not allowed |

**Description:** A theme's `expressions.json`: a face parameter preset per shared emotion name, plus theme-specific ones under `extra`. Only `neutral` is required and must set every parameter; missing shared names fall back to it. Parameters a preset leaves out keep the neutral value.

| Property                         | Pattern | Type   | Deprecated | Definition                   | Title/Description                                                               |
| -------------------------------- | ------- | ------ | ---------- | ---------------------------- | ------------------------------------------------------------------------------- |
| + [neutral](#neutral )           | No      | object | No         | In #/$defs/params            | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [happy](#happy )               | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [curious](#curious )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [thinking](#thinking )         | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [surprised](#surprised )       | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [sad](#sad )                   | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [angry](#angry )               | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [sleepy](#sleepy )             | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [scared](#scared )             | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [mischievous](#mischievous )   | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [confused](#confused )         | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [shocked](#shocked )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [excited](#excited )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [bored](#bored )               | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [skeptical](#skeptical )       | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [worried](#worried )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [disgusted](#disgusted )       | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [embarrassed](#embarrassed )   | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [proud](#proud )               | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [determined](#determined )     | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [relieved](#relieved )         | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [annoyed](#annoyed )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [suspicious](#suspicious )     | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [laughing](#laughing )         | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [disappointed](#disappointed ) | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [focused](#focused )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [nervous](#nervous )           | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [smug](#smug )                 | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |
| - [extra](#extra )               | No      | object | No         | -                            | Theme-specific expressions, e.g. \`cackle\`.                                    |

## <a name="neutral"></a>1. Property `Expressions > neutral`

|                           |                |
| ------------------------- | -------------- |
| **Type**                  | `object`       |
| **Required**              | Yes            |
| **Additional properties** | Not allowed    |
| **Defined in**            | #/$defs/params |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

| Property                               | Pattern | Type   | Deprecated | Definition                         | Title/Description       |
| -------------------------------------- | ------- | ------ | ---------- | ---------------------------------- | ----------------------- |
| - [open_l](#neutral_open_l )           | No      | number | No         | In common.json#/$defs/unit         | -                       |
| - [open_r](#neutral_open_r )           | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |
| - [tilt_l](#neutral_tilt_l )           | No      | number | No         | In common.json#/$defs/signed_unit  | -                       |
| - [tilt_r](#neutral_tilt_r )           | No      | number | No         | Same as [tilt_l](#neutral_tilt_l ) | -                       |
| - [pupil](#neutral_pupil )             | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |
| - [gaze_x](#neutral_gaze_x )           | No      | number | No         | Same as [tilt_l](#neutral_tilt_l ) | -                       |
| - [gaze_y](#neutral_gaze_y )           | No      | number | No         | Same as [tilt_l](#neutral_tilt_l ) | -                       |
| - [squint](#neutral_squint )           | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |
| - [open](#neutral_open )               | No      | number | No         | Same as [open_l](#neutral_open_l ) | Mouth opening.          |
| - [width](#neutral_width )             | No      | number | No         | Same as [open_l](#neutral_open_l ) | Mouth width.            |
| - [curve](#neutral_curve )             | No      | number | No         | Same as [tilt_l](#neutral_tilt_l ) | Smile (+) or frown (-). |
| - [asym](#neutral_asym )               | No      | number | No         | Same as [tilt_l](#neutral_tilt_l ) | -                       |
| - [teeth](#neutral_teeth )             | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |
| - [head_tilt](#neutral_head_tilt )     | No      | number | No         | Same as [tilt_l](#neutral_tilt_l ) | -                       |
| - [breath_rate](#neutral_breath_rate ) | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |
| - [blink_rate](#neutral_blink_rate )   | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |
| - [jitter](#neutral_jitter )           | No      | number | No         | Same as [open_l](#neutral_open_l ) | -                       |

### <a name="neutral_open_l"></a>1.1. Property `Expressions > neutral > open_l`

|                |                         |
| -------------- | ----------------------- |
| **Type**       | `number`                |
| **Required**   | No                      |
| **Defined in** | common.json#/$defs/unit |

| Restrictions |        |
| ------------ | ------ |
| **Minimum**  | &ge; 0 |
| **Maximum**  | &le; 1 |

### <a name="neutral_open_r"></a>1.2. Property `Expressions > neutral > open_r`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

### <a name="neutral_tilt_l"></a>1.3. Property `Expressions > neutral > tilt_l`

|                |                                |
| -------------- | ------------------------------ |
| **Type**       | `number`                       |
| **Required**   | No                             |
| **Defined in** | common.json#/$defs/signed_unit |

| Restrictions |         |
| ------------ | ------- |
| **Minimum**  | &ge; -1 |
| **Maximum**  | &le; 1  |

### <a name="neutral_tilt_r"></a>1.4. Property `Expressions > neutral > tilt_r`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [tilt_l](#neutral_tilt_l) |

### <a name="neutral_pupil"></a>1.5. Property `Expressions > neutral > pupil`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

### <a name="neutral_gaze_x"></a>1.6. Property `Expressions > neutral > gaze_x`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [tilt_l](#neutral_tilt_l) |

### <a name="neutral_gaze_y"></a>1.7. Property `Expressions > neutral > gaze_y`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [tilt_l](#neutral_tilt_l) |

### <a name="neutral_squint"></a>1.8. Property `Expressions > neutral > squint`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

### <a name="neutral_open"></a>1.9. Property `Expressions > neutral > open`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

**Description:** Mouth opening.

### <a name="neutral_width"></a>1.10. Property `Expressions > neutral > width`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

**Description:** Mouth width.

### <a name="neutral_curve"></a>1.11. Property `Expressions > neutral > curve`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [tilt_l](#neutral_tilt_l) |

**Description:** Smile (+) or frown (-).

### <a name="neutral_asym"></a>1.12. Property `Expressions > neutral > asym`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [tilt_l](#neutral_tilt_l) |

### <a name="neutral_teeth"></a>1.13. Property `Expressions > neutral > teeth`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

### <a name="neutral_head_tilt"></a>1.14. Property `Expressions > neutral > head_tilt`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [tilt_l](#neutral_tilt_l) |

### <a name="neutral_breath_rate"></a>1.15. Property `Expressions > neutral > breath_rate`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

### <a name="neutral_blink_rate"></a>1.16. Property `Expressions > neutral > blink_rate`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

### <a name="neutral_jitter"></a>1.17. Property `Expressions > neutral > jitter`

|                        |                           |
| ---------------------- | ------------------------- |
| **Type**               | `number`                  |
| **Required**           | No                        |
| **Same definition as** | [open_l](#neutral_open_l) |

## <a name="happy"></a>2. Property `Expressions > happy`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="curious"></a>3. Property `Expressions > curious`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="thinking"></a>4. Property `Expressions > thinking`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="surprised"></a>5. Property `Expressions > surprised`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="sad"></a>6. Property `Expressions > sad`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="angry"></a>7. Property `Expressions > angry`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="sleepy"></a>8. Property `Expressions > sleepy`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="scared"></a>9. Property `Expressions > scared`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="mischievous"></a>10. Property `Expressions > mischievous`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="confused"></a>11. Property `Expressions > confused`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="shocked"></a>12. Property `Expressions > shocked`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="excited"></a>13. Property `Expressions > excited`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="bored"></a>14. Property `Expressions > bored`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="skeptical"></a>15. Property `Expressions > skeptical`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="worried"></a>16. Property `Expressions > worried`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="disgusted"></a>17. Property `Expressions > disgusted`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="embarrassed"></a>18. Property `Expressions > embarrassed`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="proud"></a>19. Property `Expressions > proud`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="determined"></a>20. Property `Expressions > determined`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="relieved"></a>21. Property `Expressions > relieved`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="annoyed"></a>22. Property `Expressions > annoyed`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="suspicious"></a>23. Property `Expressions > suspicious`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="laughing"></a>24. Property `Expressions > laughing`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="disappointed"></a>25. Property `Expressions > disappointed`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="focused"></a>26. Property `Expressions > focused`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="nervous"></a>27. Property `Expressions > nervous`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="smug"></a>28. Property `Expressions > smug`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

## <a name="extra"></a>29. Property `Expressions > extra`

|                           |                                                                                    |
| ------------------------- | ---------------------------------------------------------------------------------- |
| **Type**                  | `object`                                                                           |
| **Required**              | No                                                                                 |
| **Additional properties** | [Each additional property must conform to the schema](#extra_additionalProperties) |

**Description:** Theme-specific expressions, e.g. `cackle`.

| Property                           | Pattern | Type   | Deprecated | Definition                   | Title/Description                                                               |
| ---------------------------------- | ------- | ------ | ---------- | ---------------------------- | ------------------------------------------------------------------------------- |
| - [](#extra_additionalProperties ) | No      | object | No         | Same as [neutral](#neutral ) | Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised. |

### <a name="extra_additionalProperties"></a>29.1. Property `Expressions > extra > params`

|                           |                     |
| ------------------------- | ------------------- |
| **Type**                  | `object`            |
| **Required**              | No                  |
| **Additional properties** | Not allowed         |
| **Same definition as**    | [neutral](#neutral) |

**Description:** Face parameters. Eyes and mouth in [0, 1] or [-1, 1]; global values normalised.

----------------------------------------------------------------------------------------------------------------------------
