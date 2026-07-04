export const runtime = 'nodejs';

const apiBaseUrl = process.env.API_BASE_URL || 'http://localhost:8000';

type MessagePart = {
  type?: string;
  text?: string;
};

type UIMessage = {
  role: string;
  content?: string;
  parts?: MessagePart[];
};

function lastUserText(messages: UIMessage[]): string {
  const lastUser = [...messages].reverse().find((message) => message.role === 'user');
  if (!lastUser) {
    return '';
  }
  if (lastUser.parts?.length) {
    return lastUser.parts
      .filter((part) => part.type === 'text' || part.text)
      .map((part) => part.text || '')
      .join(' ');
  }
  return lastUser.content || '';
}

export async function POST(req: Request) {
  const body = await req.json();
  const message = lastUserText(body.messages || []);
  const role = body.role || 'APP_ANALYST';
  const userId = body.user_id || 'demo_analyst';

  const response = await fetch(`${apiBaseUrl}/chat`, {
    method: 'POST',
    headers: { 'content-type': 'application/json' },
    body: JSON.stringify({
      user_id: userId,
      role,
      message,
      session_id: body.session_id || null,
    }),
  });

  if (!response.ok) {
    return new Response(`Backend chat failed with ${response.status}`, { status: 502 });
  }

  const data = await response.json();
  const text = [
    data.answer,
    '',
    `Intent: ${data.intent}`,
    `Tools: ${(data.tools_called || []).join(', ') || 'none'}`,
    `Requires approval: ${data.requires_approval ? 'yes' : 'no'}`,
    data.draft_id ? `Draft: ${data.draft_id}` : '',
    `Trace: ${data.trace_id}`,
  ]
    .filter(Boolean)
    .join('\n');

  const encoder = new TextEncoder();
  const stream = new ReadableStream({
    start(controller) {
      controller.enqueue(encoder.encode(text));
      controller.close();
    },
  });

  return new Response(stream, {
    headers: {
      'content-type': 'text/plain; charset=utf-8',
    },
  });
}
