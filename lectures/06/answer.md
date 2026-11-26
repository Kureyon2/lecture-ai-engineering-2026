# 第6回 解答

## 演習

<!-- [tool call] の行は、表示された行をそのまま貼り付けてください。終わらなかった STEP は、空欄のままでかまいません。 -->

- STEP 1 のツールの名前：
- STEP 2 の [tool call]：
- STEP 3 の [tool call]：
- STEP 4 の [tool call]：
- 気づき・疑問：

## 宿題

<!-- 基礎・実装・発展のどれか1つに取り組めば完了です。 -->

- 取り組んだレベル：基礎  
  
- やったこと：
  第3回で使用した用語集のMCPサーバーに、講義概要を取得するツールを追加した。具体的には、`app/mcp_server.py` に `server.tool()(tools.get_lecture_summary)` の1行を追加した。エージェント本体の `app/mcp_agent.py` や接続設定の `app/mcp_servers.json` は変更していない。 

- 結果：  
  `git status` で変更されたファイルが `app/mcp_server.py` のみであることを確認した。  
  `uv run python -m app.mcp_agent --list-tools` を実行すると、従来の `glossary_search_glossary` に加え、`glossary_get_lecture_summary` が表示され、利用可能なツールが2件になった。  
    次に「第2回では何を学びますか？」と質問したところ、`--trace` に以下の呼び出しが記録された。  
  ```text  
  [tool call] glossary_get_lecture_summary({'lecture': 2})  
  [tool return] glossary_get_lecture_summary -> # 第2回 ファインチューニングとLoRA  
  ```  
  取得された講義概要を基に、第2回のファインチューニングやLoRAについて回答が生成された。  
  最後に `uv run pytest -q` を実行し、21件すべてのテストが合格した。  
  
- 気づき・疑問：
  今回の宿題では、MCPサーバー側に1行追加するだけで、エージェント側のコードや設定を変更せずに新しいツールが利用できることを確認できた。  
  第5回までのようにエージェントへ関数を直接登録する方法と異なり、MCPではツールをサーバー側で公開し、エージェントが起動時に利用可能なツールを取得する仕組みになっていることを理解した。  
  一方、ツールを追加するだけで機能を拡張できる反面、公開するツールが増えた場合に、モデルが適切なツールを選択できるか、また権限や安全性をどう管理すべきかが重要になると感じた。  