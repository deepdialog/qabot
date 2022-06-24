
import { useState } from "react"
import { Input, Button, message, Form } from 'antd'


export function AddPair(props) {

    let mode
    if (props.id) {
        mode = 'edit'
    } else {
        mode = 'create'
    }

    const [question, setQuestion] = useState(props.question ?? '')
    const [answer, setAnswer] = useState(props.answer ?? '')
    const [url, setUrl] = useState(props.url ?? '')
    const { token } = props

    const formItemLayout = {
        labelCol: {
            span: 4 + 4,
        },
        wrapperCol: {
            span: 8,
        },
    }
    const buttonItemLayout = {
        wrapperCol: {
            span: 16,
            offset: 4,
        },
    }

    return (
        <div>
            <Form
                {...formItemLayout}
                layout='horizontal'
            >
                <Form.Item label="问题" name="layout">
                    <Input
                        value={question}
                        onChange={e => setQuestion(e.target.value)}
                        placeholder='问题'
                    />
                </Form.Item>
                <Form.Item label="回答" name="layout">
                    <Input.TextArea
                        value={answer}
                        onChange={e => setAnswer(e.target.value)}
                        placeholder='回答'
                    />
                </Form.Item>
                <Form.Item label="URL" name="layout">
                    <Input
                        value={url}
                        onChange={e => setUrl(e.target.value)}
                        placeholder='URL（可选）'
                    />
                </Form.Item>
                <Form.Item name="layout" {...buttonItemLayout}>
                    <Button
                        onClick={async () => {
                            let api
                            if (mode === 'create') {
                                api = `/api/qabot/pair/${token}`
                            } else {
                                api = `/api/qabot/pair/${token}/${props.id}`
                            }
                            const res = await fetch(api, {
                                method: mode === 'create' ? 'POST' : 'PUT',
                                headers: {
                                    'Content-Type': 'application/json',
                                },
                                body: JSON.stringify({
                                    question,
                                    answer,
                                    parent: null,
                                    url,
                                })
                            })
                            const ret = await res.json()
                            if (ret.ok) {
                                message.success(mode === 'create' ?  '添加成功' : '修改成功')
                            } else {
                                message.error(ret.error || '未知错误')
                            }
                            if (props.onSaved) {
                                props.onSaved(ret.ok)
                            }
                        }}
                    >
                        {mode === 'create' ?  '添加' : '修改'}
                    </Button>
                </Form.Item>
            </Form>
        </div>
    )
}
