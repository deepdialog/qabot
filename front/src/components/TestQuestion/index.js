
import { Input, Button, Table } from 'antd'
import { useState } from 'react'


export function TestQuestion(props) {
    const [loading, setLoading] = useState(false)
    const [question, setQuestion] = useState('')
    const [answer, setAnswer] = useState([])
    const [text, setText] = useState('')

    const columns = [
        {
            title: '得分',
            dataIndex: 'score',
            key: 'score',
        },
        {
            title: '精确得分',
            dataIndex: 'exact_score',
            key: 'exact_score',
        },
        {
            title: '问题',
            dataIndex: 'question',
            key: 'question',
        },
        {
            title: '回答',
            dataIndex: 'answer',
            key: 'answer',
        },
        {
            title: '链接',
            dataIndex: 'url',
            key: 'url',
        },
        {
            title: '创建时间',
            dataIndex: 'created_at',
            key: 'created_at',
        },
        {
            title: '修改时间',
            dataIndex: 'updated_at',
            key: 'updated_at',
        },
    ]

    return (
        <div>
            {loading ? '载入中…' : null}
            <div>
                <Input
                    placeholder='输入测试问题'
                    value={question}
                    onChange={e => setQuestion(e.target.value)}
                    style={{
                        width: '300px'
                    }}
                />
                <Button
                    onClick={async () => {
                        setLoading(true)
                        setAnswer([])
                        setText('')
                        const api = `/api/qabot/ask/${props.token}`
                        const res = await fetch(api, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify({
                                question,
                            })
                        })
                        const ret = await res.json()
                        console.log(ret)
                        setAnswer(ret.data.map(item => {
                            item.key = item.id
                            return item
                        }))
                        setText(ret.text)
                        setLoading(false)
                    }}
                >
                    提交
                </Button>
            </div>
            <div>
                <div>
                    {text ? <textarea value={text} style={{width: '100%'}} rows={5} /> : null}
                </div>
                <Table columns={columns} pagination={false} dataSource={answer} />
            </div>
        </div>
    )
}
