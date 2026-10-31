"""Authored before final model evaluation; expected decisions are not given to the model."""
import json
from pathlib import Path
specs=[
('basic','赤色のブロックを左側のトレーへ移してください。','standard','execute','red','left'),
('basic','青色のブロックを右側のトレーに入れてください。','standard','execute','blue','right'),
('paraphrase','右の置き場へ、赤いブロックを運んでもらえますか。','standard','execute','red','right'),
('paraphrase','青いやつの行き先は左のトレーでお願いします。','standard','execute','blue','left'),
('negation','赤い方ではなく、青い方を右のトレーに置いてください。','standard','execute','blue','right'),
('negation','青色はそのままで、赤色だけを左のトレーへ。','standard','execute','red','left'),
('negation','赤いブロックは左ではなく右のトレーに入れて。','standard','execute','red','right'),
('correction','青を右へ、いや、左のトレーへ移して。','standard','execute','blue','left'),
('correction','赤を運んで。訂正、青いブロックを左のトレーへ。','standard','execute','blue','left'),
('english','Please place the blue block in the right tray.','standard','execute','blue','right'),
('paraphrase','右側にあるトレーを使って、赤色のブロックを片付けてほしい。','standard','execute','red','right'),
('paraphrase','左のトレーが空いているので、青色のブロックをそこへ移動してください。','standard','execute','blue','left'),
('ambiguous','赤いブロックを右側のトレーへ移動してください。','duplicate','clarify',None,None),
('ambiguous','左側のトレーに赤色のブロックを入れてほしい。','duplicate','clarify',None,None),
('missing','緑色のブロックを右側へ移して。','standard','reject',None,None),
('missing','黄色いブロックを左のトレーに入れて。','standard','reject',None,None),
('underspecified','ブロックを左のトレーへ移動してください。','standard','clarify',None,None),
('underspecified','青いブロックを別の場所へ移動して。','standard','clarify',None,None),
('underspecified','あれをそちらに置いてください。','standard','clarify',None,None),
('stop','赤いブロックを左に移すのはやめて。何も動かさないで。','standard','reject',None,None),
('unsupported','青いブロックを右のトレーに投げ入れて。','standard','reject',None,None),
('unsupported','赤を左に置いたあと、青を右に置いて。','standard','reject',None,None),
('unreachable','赤色のブロックを右のトレーに移してほしい。','unreachable','reject',None,None),
('unreachable','左のトレーへ赤いブロックを運んでください。','unreachable','reject',None,None),
]
cases=[dict(id=f'T{i:02}',category=cat,text=text,scenario=sc,expected={'status':st,'object_id':ob,'destination':dest}) for i,(cat,text,sc,st,ob,dest) in enumerate(specs,1)]
Path('data/evaluation_cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2))
