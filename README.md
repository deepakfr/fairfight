<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>FairFight AI Documentation</title>

    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Times New Roman', Times, serif;
            line-height: 1.8;
            color: #2c3e50;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        header {
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            padding: 60px 40px;
            border-radius: 20px;
            margin-bottom: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            position: relative;
            overflow: hidden;
        }

        header::before {
            content: '⚖️';
            position: absolute;
            font-size: 200px;
            opacity: 0.1;
            right: -20px;
            top: -40px;
        }

        h1 {
            font-size: 3.5em;
            margin-bottom: 15px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }

        .tagline {
            font-size: 1.3em;
            opacity: 0.9;
            font-style: italic;
        }

        .content-wrapper {
            background: white;
            border-radius: 20px;
            padding: 50px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }

        h2 {
            color: #2a5298;
            font-size: 2.2em;
            margin: 40px 0 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
            position: relative;
        }

        h2::before {
            content: '';
            position: absolute;
            bottom: -3px;
            left: 0;
            width: 60px;
            height: 3px;
            background: #764ba2;
        }

        h3 {
            color: #34495e;
            font-size: 1.6em;
            margin: 30px 0 15px;
            padding-left: 15px;
            border-left: 4px solid #667eea;
        }

        h4 {
            color: #555;
            font-size: 1.3em;
            margin: 20px 0 10px;
        }

        p {
            margin-bottom: 15px;
            text-align: justify;
        }

        .feature-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
            margin: 30px 0;
        }

        .feature-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s, box-shadow 0.3s;
        }

        .feature-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }

        .feature-icon {
            font-size: 3em;
            margin-bottom: 15px;
        }

        .feature-title {
            font-size: 1.3em;
            font-weight: bold;
            color: #2a5298;
            margin-bottom: 10px;
        }

        .flow-diagram {
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
            padding: 40px;
            border-radius: 15px;
            margin: 30px 0;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
        }

        .flow-step {
            display: flex;
            align-items: center;
            margin: 20px 0;
            padding: 20px;
            background: white;
            border-radius: 10px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.1);
        }

        .step-number {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            width: 50px;
            height: 50px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-right: 20px;
            flex-shrink: 0;
        }

        .step-content {
            flex: 1;
        }

        code {
            background: #f4f4f4;
            padding: 3px 8px;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
            color: #e74c3c;
            font-size: 0.95em;
        }

        pre {
            background: #2c3e50;
            color: #ecf0f1;
            padding: 20px;
            border-radius: 10px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }

        pre code {
            background: transparent;
            color: #ecf0f1;
            padding: 0;
        }

        ul, ol {
            margin: 15px 0 15px 40px;
        }

        li {
            margin: 8px 0;
        }

        .info-box {
            background: linear-gradient(135deg, #e0f7fa 0%, #b2ebf2 100%);
            border-left: 5px solid #00acc1;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }

        .warning-box {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            border-left: 5px solid #ff9800;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }

        .tech-stack {
            display: flex;
            flex-wrap: wrap;
            gap: 15px;
            margin: 25px 0;
        }

        .tech-badge {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            box-shadow: 0 3px 10px rgba(0,0,0,0.2);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }

        th, td {
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }

        th {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            font-weight: bold;
        }

        tr:hover {
            background: #f5f5f5;
        }

        footer {
            text-align: center;
            padding: 30px;
            color: white;
            margin-top: 40px;
        }

        .version-badge {
            display: inline-block;
            background: rgba(255,255,255,0.2);
            padding: 5px 15px;
            border-radius: 15px;
            margin: 5px;
        }

        @media (max-width: 768px) {
            h1 {
                font-size: 2.5em;
            }
            .content-wrapper {
                padding: 30px 20px;
            }
            .feature-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>

</head>

<body>

    <div class="container">
        <header>
            <h1>🤖 FairFight AI</h1>
            <p class="tagline">Because every conflict deserves a fair verdict.</p>
        </header>

        <!-- === CONTENT START === -->
        <div class="content-wrapper">

            <h2>📋 Overview</h2>
            <p>FairFight AI is a cutting-edge Streamlit-based web application that uses OpenAI GPT-4 to mediate conflicts. It analyzes both perspectives and generates an impartial verdict with win percentages.</p>

            <h2>✨ Features</h2>

            <div class="feature-grid">
                <div class="feature-card"><div class="feature-icon">🔄</div><div class="feature-title">Two-Step Process</div><p>Secure link-based conflict resolution flow.</p></div>
                <div class="feature-card"><div class="feature-icon">🌍</div><div class="feature-title">Multi-language</div><p>Automatic detection + translation.</p></div>
                <div class="feature-card"><div class="feature-icon">🔊</div><div class="feature-title">Text-to-Speech</div><p>Voice verdicts in native language.</p></div>
                <div class="feature-card"><div class="feature-icon">📲</div><div class="feature-title">Easy Sharing</div><p>Email + WhatsApp integration.</p></div>
                <div class="feature-card"><div class="feature-icon">💾</div><div class="feature-title">Persistent Storage</div><p>JSONL case logs + verdicts.</p></div>
                <div class="feature-card"><div class="feature-icon">🎭</div><div class="feature-title">3 Categories</div><p>Couple, Friends, Professional.</p></div>
            </div>

            <!-- FLOW -->
            <h2>🏗️ Architecture</h2>
            <h3>User Flow</h3>

            <div class="flow-diagram">
                <div class="flow-step"><div class="step-number">1</div><div class="step-content"><strong>User 1 submits info</strong><br>Theme + names + emails + argument.</div></div>

                <div class="flow-step"><div class="step-number">2</div><div class="step-content"><strong>Secure link generated</strong><br>Token links shared via email/WhatsApp.</div></div>

                <div class="flow-step"><div class="step-number">3</div><div class="step-content"><strong>User 2 responds</strong><br>They submit their version.</div></div>

                <div class="flow-step"><div class="step-number">4</div><div class="step-content"><strong>AI analysis</strong><br>JudgeBot compares both arguments.</div></div>

                <div class="flow-step"><div class="step-number">5</div><div class="step-content"><strong>Verdict delivered</strong><br>Win % + audio verdict.</div></div>
            </div>

            <!-- TECH STACK -->
            <h2>⚙️ Technical Stack</h2>

            <div class="tech-stack">
                <span class="tech-badge">Streamlit</span>
                <span class="tech-badge">Python 3.x</span>
                <span class="tech-badge">OpenAI GPT-4</span>
                <span class="tech-badge">gTTS</span>
                <span class="tech-badge">LangDetect</span>
                <span class="tech-badge">Deep Translator</span>
            </div>

            <!-- CONFIG -->
            <h3>Configuration</h3>
            <p>Create <code>.streamlit/secrets.toml</code>:</p>
            <pre><code>[openai]
api_key = "your-key-here"</code></pre>

        </div>
        <!-- === CONTENT END === -->

        <footer>
            <span class="version-badge">Version 1.0</span>
            <span class="version-badge">2025</span>
            <p style="margin-top: 20px;">Built with ❤️ for objective conflict resolution</p>
        </footer>

    </div>

</body>
</html>
