
import ExcelJS from 'exceljs'
import { useParams } from 'react-router-dom'
import { Upload, Button, Table } from 'antd'
import { UploadOutlined } from '@ant-design/icons'
import { useState } from 'react'

import { Header } from '../components/Header'


export default function BatchInsert(props) {
    const { token } = useParams()
    const [data, setData] = useState([])
    const [uploading, setUploading] = useState(false)
    const [done, setDone] = useState(0)
    const [total, setTotal] = useState(0)

    const columns = [
        {
            title: '问题',
            dataIndex: 'question',
            key: 'question',
        },
        {
            title: '答案',
            dataIndex: 'answer',
            key: 'answer',
        },
        {
            title: 'URL',
            dataIndex: 'url',
            key: 'url',
        },
        {
            title: '状态',
            dataIndex: 'status',
            key: 'status',
        },
    ]

    return (
        <div>
            <Header token={token} />
            批量添加
            <Upload
                beforeUpload={() => false}
                action=''
                onChange={info => {
                    const file = info.fileList[0].originFileObj
                    const fr = new FileReader()
                    fr.onload = () => {
                        const wb = new ExcelJS.Workbook()
                        wb.xlsx.load(fr.result).then(() => {
                            const body = []
                            const worksheet = wb.worksheets[0]
                            worksheet.eachRow((row, rowNumber) => {
                                if (rowNumber <= 1) {
                                    return
                                }
                                const obj = {
                                    key: rowNumber,
                                    question: row.getCell(1).value,
                                    answer: row.getCell(2).value,
                                    url: row.getCell(3).value,
                                    status: '',
                                }
                                if (obj.answer && obj.answer.text) {
                                    obj.answer = obj.answer.text
                                }
                                if (obj.url && obj.url.hyperlink) {
                                    obj.url = obj.url.hyperlink
                                }
                                body.push(obj)
                            })
                            // console.log(body)
                            setData(body)
                            setTotal(body.length)
                        })
                    }
                    fr.readAsArrayBuffer(file)
                }}
            >
                <Button icon={<UploadOutlined />}>Click to Upload</Button>
            </Upload>
            {data.length > 0 ? (
                <div>
                    <label>
                        导入了 {done} 条
                        总计 {total} 条
                    </label>
                    <Button
                        disabled={uploading}
                        onClick={async () => {
                            setUploading(true)
                            setDone(0)
                            let c = 0
                            for (const item of data) {
                                const api = `/api/qabot/pair/${token}`
                                const res = await fetch(api, {
                                    method: 'POST',
                                    headers: {
                                        'Content-Type': 'application/json',
                                    },
                                    body: JSON.stringify({
                                        question: item.question,
                                        answer: item.answer,
                                        parent: null,
                                        url: item.url,
                                    })
                                })
                                const ret = await res.json()
                                if (ret.ok) {
                                    item.status = '添加成功'
                                } else {
                                    item.status = ret.error || '未知错误'
                                }
                                c++
                                setDone(c)
                            }
                            setUploading(false)
                        }}
                    >
                        开始导入
                    </Button>
                </div>
            ) : null}
            <Table columns={columns} dataSource={data} pagination={false} />
        </div>
    )
}