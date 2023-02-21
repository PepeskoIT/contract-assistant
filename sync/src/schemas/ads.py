from datetime import datetime
from typing import List, Optional

from schemas.common import Base
from sqlalchemy import (
    BigInteger, ForeignKey, Integer, Sequence, String, func, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

ad_id_seq = Sequence("ad_id_seq", metadata=Base.metadata, start=1)
company_id_seq = Sequence(
        "company_id_seq", metadata=Base.metadata, start=1
    )


class Ad(Base):
    __tablename__ = 'ads'
    __table_args__ = (
        UniqueConstraint(
            "ad_src", "ad_url", "ad_posted_date"
        ),
    )

    ad_company: Mapped["Company"] = relationship(
        back_populates="company_ads", lazy="selectin"
    )
    ad_company_id = mapped_column(ForeignKey("companies.company_id"))
    ad_category: Mapped[Optional[str]]
    ad_created_date: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    ad_expired: Mapped[Optional[bool]]
    ad_fully_remote: Mapped[Optional[bool]]
    ad_id = mapped_column(
        BigInteger, ad_id_seq, server_default=ad_id_seq.next_value(),
        primary_key=True
    )
    ad_main_technology: Mapped[Optional[str]] = mapped_column(String(32))
    ad_online_intereview: Mapped[Optional[bool]]
    ad_posted_date: Mapped[datetime]
    ad_b2b_available: Mapped[Optional[bool]]
    ad_permanent_available: Mapped[Optional[bool]]
    ad_salary_b2b_currency: Mapped[Optional[str]]
    ad_salary_b2b_from: Mapped[Optional[int]]
    ad_salary_b2b_to: Mapped[Optional[int]]
    ad_salary_permanent_from: Mapped[Optional[int]]
    ad_salary_permanent_currency: Mapped[Optional[str]]
    ad_salary_permanent_to: Mapped[Optional[int]]
    ad_src: Mapped[str]
    ad_title: Mapped[str]
    ad_url: Mapped[str]


class Company(Base):
    __tablename__ = 'companies'
    __table_args__ = (
        UniqueConstraint(
            "company_name", "company_hq_country", "company_hq_city"
        ),
    )

    company_ads: Mapped[List["Ad"]] = relationship(
        back_populates="ad_company", lazy="selectin"
    )

    company_created_date: Mapped[datetime] = mapped_column(
        insert_default=func.now()
    )
    company_hq_city: Mapped[Optional[str]]
    company_hq_country: Mapped[Optional[str]]
    company_id = mapped_column(Integer, company_id_seq, primary_key=True)
    company_name: Mapped[str]
    company_size: Mapped[Optional[int]]
    company_url: Mapped[Optional[str]]
