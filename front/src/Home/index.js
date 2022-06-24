
// import { Link } from 'react-router-dom'
import { Table, Pagination, Button, message } from 'antd'
import { useParams, useNavigate } from 'react-router-dom'
import { Input, Card } from 'antd'
import { useState, useEffect } from "react"

import { AddPair } from '../components/AddPair'
import { Header } from '../components/Header'


/**
 * 更新数据
 */
async function updateData(setLoading, token, page, pageSize, setData, setTotal) {
    setLoading(true)
    const res = await fetch(`/api/qabot/pair/${token}/${page}/${pageSize}`)
    const ret = await res.json()
    console.log(ret)
    setData(ret.data.map(item => {
        item.key = item.id
        return item
    }))
    setTotal(ret.total)
    setLoading(false)
}

export default function Home() {
    const { token } = useParams()
    const navigate = useNavigate()
    const [loading, setLoading] = useState(true)
    const [page, setPage] = useState(0)
    const [data, setData] = useState([])
    const [total, setTotal] = useState(0)
    const [pageSize, setPageSize] = useState(20)
    const [edit, setEdit] = useState(null)

    useEffect(() => {
        updateData(setLoading, token, page, pageSize, setData, setTotal)
    }, [token, page, pageSize])

    if (!token) {
        return (
            <div>
                <Input.Search
                    style={{
                        width: '300px'
                    }}
                    placeholder='请输入token'
                    enterButton='确定'
                    onSearch={token => {
                        navigate(`/home/${token}`)
                    }}
                />
            </div>
        )
    }

    const columns = [
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
        {
            title: '管理',
            dataIndex: 'id',
            key: 'id',
            render: (id, obj) => {
                return (
                    <div>
                        <Button
                            onClick={() => {
                                setEdit(obj)
                            }}
                        >
                            修改
                        </Button>
                        <Button
                            onClick={async () => {
                                const api = `/api/qabot/pair/${token}/${id}`
                                const res = await fetch(api, {
                                    method: 'DELETE',
                                })
                                const ret = await res.json()
                                if (ret.ok) {
                                    message.success('删除成功')
                                    updateData(setLoading, token, page, pageSize, setData, setTotal)
                                } else {
                                    message.error(ret.error || '未知错误')
                                }
                            }}
                        >
                            删除
                        </Button>
                    </div>
                )
            },
        }
    ]

    return (
        <div>
            <Header token={token} />
            <Card
                title='添加问答对'
            >
                {edit ? (
                    <AddPair
                        {...edit}
                        token={token}
                        onSaved={() => {
                            setEdit(null)
                            if (page !== 0) {
                                setPage(0)
                            } else {
                                updateData(setLoading, token, page, pageSize, setData, setTotal)
                            }
                        }}
                    />
                ) : (
                    <AddPair
                        token={token}
                        onSaved={() => {
                            if (page !== 0) {
                                setPage(0)
                            } else {
                                updateData(setLoading, token, page, pageSize, setData, setTotal)
                            }
                        }}
                    />
                )}
            </Card>

            <Card
                title='当前问答数据'
            >
                {loading ? '载入中...' : null}
                <Table columns={columns} dataSource={data} pagination={false} />
                <Pagination
                    current={page + 1}
                    total={total}
                    onChange={(page, pageSize) => {
                        setPage(page - 1)
                        setPageSize(pageSize)
                    }}
                    pageSize={pageSize}
                />
            </Card>
        </div>
    )
}
